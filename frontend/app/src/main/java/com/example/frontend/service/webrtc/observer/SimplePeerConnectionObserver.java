package com.example.frontend.service.webrtc.observer;

import android.util.Log;

import com.example.frontend.databinding.ActivitySamplePeerConnectionBinding;

import org.json.JSONException;
import org.json.JSONObject;
import org.webrtc.DataChannel;
import org.webrtc.IceCandidate;
import org.webrtc.MediaStream;
import org.webrtc.MediaStreamTrack;
import org.webrtc.PeerConnection;
import org.webrtc.RtpReceiver;
import org.webrtc.VideoTrack;

import java.util.Arrays;

public class SimplePeerConnectionObserver implements PeerConnection.Observer {
    private final String TAG;
    private final ActivitySamplePeerConnectionBinding binding;
    private final Runnable onIceGatheringComplete;

    public SimplePeerConnectionObserver(String TAG, ActivitySamplePeerConnectionBinding binding, Runnable onIceGatheringComplete) {
        super();
        this.TAG = TAG;
        this.binding = binding;
        this.onIceGatheringComplete = onIceGatheringComplete;
    }

    @Override
    public void onSignalingChange(PeerConnection.SignalingState signalingState) {
        Log.i(TAG, "onSignalingChange: " + signalingState);
    }

    @Override
    public void onIceConnectionChange(PeerConnection.IceConnectionState iceConnectionState) {
        Log.i(TAG, "onIceConnectionChange: " + iceConnectionState);
    }

    @Override
    public void onIceConnectionReceivingChange(boolean b) {
        Log.i(TAG, "onIceConnectionReceivingChange: " + b);
    }

    @Override
    public void onIceGatheringChange(PeerConnection.IceGatheringState iceGatheringState) {
        Log.i(TAG, "onIceGatheringChange: " + iceGatheringState);
        if(iceGatheringState == PeerConnection.IceGatheringState.COMPLETE) {
            onIceGatheringComplete.run();
        }
    }

    @Override
    public void onIceCandidate(IceCandidate iceCandidate) {
        Log.i(TAG, "onIceCandidate: " + iceCandidate);

        JSONObject message = new JSONObject();

        try {
            message.put("type", "candidate");
            message.put("label", iceCandidate.sdpMLineIndex);
            message.put("id", iceCandidate.sdpMid);
            message.put("candidate", iceCandidate.sdp);

            //Log.i(TAG, "onIceCandidate: sending candidate " + message);
            //sendMessage(message);
        } catch (JSONException e) {
            e.printStackTrace();
        }
    }

    @Override
    public void onIceCandidatesRemoved(IceCandidate[] iceCandidates) {
        Log.i(TAG, "onIceCandidatesRemoved: " + Arrays.toString(iceCandidates));
    }

    @Override
    public void onAddStream(MediaStream mediaStream) {
        Log.i(TAG, "onAddStream: " + mediaStream.videoTracks.size());
    }

    @Override
    public void onRemoveStream(MediaStream mediaStream) {
        Log.i(TAG, "onRemoveStream size: " + mediaStream.videoTracks.size());
    }

    @Override
    public void onDataChannel(DataChannel dataChannel) {
        Log.i(TAG, "onDataChannel: " + dataChannel);
    }

    @Override
    public void onRenegotiationNeeded() {
        Log.i(TAG, "onRenegotiationNeeded: ");
    }

    @Override
    public void onAddTrack(RtpReceiver rtpReceiver, MediaStream[] mediaStreams) {
        Log.i(TAG, "onAddTrack: Receiver:" + rtpReceiver.id() + " Streams: " + mediaStreams.length);
        MediaStreamTrack track = rtpReceiver.track();
        if (track instanceof VideoTrack) {
            VideoTrack remoteVideoTrack = (VideoTrack) track;
            remoteVideoTrack.setEnabled(true);
            remoteVideoTrack.addSink(binding.surfaceView2);
        }
    }
}
