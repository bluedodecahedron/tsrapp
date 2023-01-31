package com.example.frontend.activity.tsdr.webrtc.observers;

import android.util.Log;

import com.example.frontend.databinding.ActivityWebrtcBinding;

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

public class CustomPeerConnectionObserver implements PeerConnection.Observer {
    private final String TAG;
    private final ActivityWebrtcBinding binding;
    private final Runnable onIceGatheringComplete;

    public CustomPeerConnectionObserver(String TAG, ActivityWebrtcBinding binding, Runnable onIceGatheringComplete) {
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
    }

    @Override
    public void onIceCandidate(IceCandidate iceCandidate) {
        Log.i(TAG, "onIceCandidate: " + iceCandidate);
        onIceGatheringComplete.run();
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
            remoteVideoTrack.addSink(binding.surfaceRenderer);
        }
    }
}
