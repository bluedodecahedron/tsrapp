# Code portions taken from the aiortc server example:
# https://github.com/aiortc/aiortc/tree/main/examples/server

import asyncio
import logging
import time
import uuid
import traceback
import signal

import aiortc.codecs.h264
import cv2
import app.apps.tsdr.services as services
from av import VideoFrame
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaBlackhole, MediaRecorder, MediaRelay
from aiortc.rtcrtpsender import RTCRtpSender


logger = logging.getLogger('backend')
aiortc.codecs.vpx.MIN_BITRATE = 1000000
aiortc.codecs.vpx.DEFAULT_BITRATE = 3000000
aiortc.codecs.vpx.MAX_BITRATE = 5000000
aiortc.codecs.vpx.MAX_FRAME_RATE = 20
aiortc.codecs.vpx.PACKET_MAX = 700
aiortc.codecs.h264.MIN_BITRATE = 1000000
aiortc.codecs.h264.DEFAULT_BITRATE = 3000000
aiortc.codecs.h264.MAX_BITRATE = 3000000
aiortc.codecs.h264.MAX_FRAME_RATE = 20
aiortc.codecs.h264.PACKET_MAX = 700
pcs = set()
relay = MediaRelay()


class FPSTimer:
    def __init__(self):
        self.frame_counter = 0
        self.start_time = time.time()

    def add_frame(self):
        self.frame_counter = self.frame_counter + 1

    def get_time_difference(self):
        return time.time() - self.start_time

    def get_fps(self):
        return self.frame_counter/self.get_time_difference()

    def reset(self):
        self.frame_counter = 0
        self.start_time = time.time()


fpsTimer = FPSTimer()


class VideoTransformTrack(MediaStreamTrack):
    """
    A video stream track that transforms frames from another track.
    """

    kind = "video"

    def __init__(self, track, transform, pc, tsdr_state):
        super().__init__()  # don't forget this!
        self.track = track
        self.transform = transform
        self.pc = pc
        self.tsdr_state = tsdr_state

    async def recv(self):
        frame = await self.track.recv()
        start_time = time.perf_counter()
        img = frame.to_ndarray(format="bgr24").copy()

        # perform some sort of image processing
        if self.transform == "tsdr":
            # perform traffic sign detection
            try:
                # class_ids, img = services.tsdr(img)
                img = self.tsdr_state.update(img)
            except:
                traceback.print_exc()

            # rebuild a VideoFrame, preserving timing information
            new_frame = VideoFrame.from_ndarray(img, format="bgr24")
            new_frame.pts = frame.pts
            new_frame.time_base = frame.time_base
        elif self.transform == "edges":
            # perform edge detection
            img = cv2.cvtColor(cv2.Canny(img, 100, 200), cv2.COLOR_GRAY2BGR)

            # rebuild a VideoFrame, preserving timing information
            new_frame = VideoFrame.from_ndarray(img, format="bgr24")
            new_frame.pts = frame.pts
            new_frame.time_base = frame.time_base
        else:
            # leave frame unchanged
            new_frame = frame

        fpsTimer.add_frame()
        # print some stats every second
        if fpsTimer.get_time_difference() > 1.0:
            # print fps
            logger.info("FPS: " + str(fpsTimer.get_fps()))
            fpsTimer.reset()
            # save frame
            # services.save_result(img)
            # print frame processing time
            logger.info("Frame processing took: {:.4f}s".format(time.perf_counter() - start_time))
            # print pc stats
            sender = self.pc.getSenders()[0]
            stats = await sender.getStats()
            logger.info("Sender stats: \n" + str(stats))

        return new_frame


def force_codec(pc, sender, forced_codec):
    kind = forced_codec.split("/")[0]
    codecs = RTCRtpSender.getCapabilities(kind).codecs
    transceiver = next(t for t in pc.getTransceivers() if t.sender == sender)
    pref = [codec for codec in codecs if codec.mimeType == forced_codec]
    transceiver.setCodecPreferences(pref)


async def offer(offer_schema):
    signal.signal(signal.SIGINT, on_shutdown)
    signal.signal(signal.SIGTERM, on_shutdown)

    offer = RTCSessionDescription(sdp=offer_schema.sdp, type=offer_schema.type)
    record_to = None

    pc = RTCPeerConnection()
    pc_id = "PeerConnection(%s)" % uuid.uuid4()
    pcs.add(pc)

    def log_info(msg, *args):
        logger.info(pc_id + " " + msg, *args)

    # prepare local media
    if record_to:
        recorder = MediaRecorder(record_to)
    else:
        recorder = MediaBlackhole()

    @pc.on("datachannel")
    def on_datachannel(channel):
        @channel.on("message")
        def on_message(message):
            if isinstance(message, str) and message.startswith("ping"):
                channel.send("pong" + message[4:])

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        log_info("Connection state is %s", pc.connectionState)
        if pc.connectionState == "failed":
            await pc.close()
            pcs.discard(pc)
        elif pc.connectionState == "connected":
            sender = pc.getSenders()[0]
            stats = await sender.getStats()
            logger.info("Sender stats: \n" + str(stats))

    @pc.on("track")
    def on_track(track):
        log_info("Track %s received", track.kind)
        tsdr_state = services.TsdrState()

        if track.kind == "video":
            video_sender = pc.addTrack(
                VideoTransformTrack(
                    relay.subscribe(track),
                    transform=offer_schema.video_transform,
                    pc=pc,
                    tsdr_state=tsdr_state
                )
            )
            # force_codec(pc, video_sender, 'video/H264')
            if record_to:
                recorder.addTrack(relay.subscribe(track))

        @track.on("ended")
        async def on_ended():
            log_info("Track %s ended", track.kind)
            await recorder.stop()
            await pc.close()
            tsdr_state.release()


    # handle offer
    await pc.setRemoteDescription(offer)
    logger.info("OFFER SDP: \n" + offer.sdp)
    await recorder.start()

    # send answer
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    logger.info("ANSWER SDP: \n" + offer.sdp)

    sdp = {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
    return sdp


def on_shutdown(*args):
    # close peer connections
    logger.info("Closing any remaining peer connections")
    coros = [pc.close() for pc in pcs]
    asyncio.gather(*coros)
