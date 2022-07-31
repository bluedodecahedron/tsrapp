package com.example.frontend.activity.tsdr.webrtc.video;

import android.app.Activity;
import android.util.Log;

import com.example.frontend.R;
import com.example.frontend.databinding.ActivityWebrtcBinding;

import org.webrtc.PeerConnection;
import org.webrtc.RTCStats;
import org.webrtc.RTCStatsCollectorCallback;
import org.webrtc.RTCStatsReport;

import java.math.BigInteger;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.Map;

public class StatisticsRenderer {
    private static final int UPDATE_DELAY = 1000;

    private BigInteger bytesSent = BigInteger.ZERO;
    private BigInteger bytesReceived = BigInteger.ZERO;
    private LocalDateTime lastUpdate = LocalDateTime.now();
    private LocalDateTime lastBandwidthUpdate = LocalDateTime.now();
    private LocalDateTime lastFpsUpdate = LocalDateTime.now();
    private int frame_counter = 0;

    private final Activity activity;
    private final ActivityWebrtcBinding binding;
    private final PeerConnection localPeerConnection;
    private final String TAG;

    public StatisticsRenderer(Activity activity, ActivityWebrtcBinding binding, PeerConnection localPeerConnection, String TAG) {
        this.activity = activity;
        this.binding = binding;
        this.localPeerConnection = localPeerConnection;
        this.TAG = TAG;
    }

    public boolean isUpdate() {
        long timeSinceUpdate = ChronoUnit.MILLIS.between(lastUpdate, LocalDateTime.now());
        return timeSinceUpdate > UPDATE_DELAY;
    }

    public void update() {
        lastUpdate = LocalDateTime.now();
        updateFps();
        updateBandwidth();
    }

    public void incrementFrameCounter() {
        frame_counter++;
    }

    private void updateFps() {
        float delay = ChronoUnit.MILLIS.between(lastFpsUpdate, LocalDateTime.now()) / 1000.0F;
        float fps = frame_counter / delay;
        lastFpsUpdate = LocalDateTime.now();
        updateFpsUi(fps);
        frame_counter = 0;
    }

    private void updateFpsUi(float fps) {
        //runOnUiThread because only the original thread that created a view hierarchy can touch its views
        activity.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                binding.fpsCounter.setText(activity.getString(R.string.fps_counter, fps));
            }
        });
    }

    private void updateBandwidth() {
        //runOnUiThread because only the original thread that created a view hierarchy can touch its views
        activity.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                localPeerConnection.getStats(new RTCStatsCollectorCallback() {
                    @Override
                    public void onStatsDelivered(RTCStatsReport rtcStatsReport) {
                        StatisticsRenderer.this.onStatsDelivered(rtcStatsReport);
                    }
                });
            }
        });
    }

    public void onStatsDelivered(RTCStatsReport rtcStatsReport) {
        Map<String, RTCStats> statsmap = rtcStatsReport.getStatsMap();
        for(RTCStats rtcStats : statsmap.values()) {
            if (rtcStats.getType().equals("candidate-pair")) {
                Map<String, Object> members = rtcStats.getMembers();
                String state = (String)members.get("state");
                if(state != null && state.equals("succeeded")) {
                    BigInteger bytesSent = (BigInteger) members.get("bytesSent");
                    BigInteger bytesReceived = (BigInteger) members.get("bytesReceived");
                    if(bytesSent != null && bytesReceived != null) {
                        BigInteger bytesSentDiff = bytesSent.subtract(StatisticsRenderer.this.bytesSent);
                        BigInteger bytesReceivedDiff = bytesReceived.subtract(StatisticsRenderer.this.bytesReceived);
                        long updateDelay = ChronoUnit.MILLIS.between(lastBandwidthUpdate, LocalDateTime.now());
                        //dividing bytes by milliseconds is the same as dividing kilobytes by seconds
                        BigInteger uploadRate = bytesSentDiff.divide(BigInteger.valueOf(updateDelay));
                        BigInteger downloadRate = bytesReceivedDiff.divide(BigInteger.valueOf(updateDelay));

                        StatisticsRenderer.this.bytesSent = bytesSent;
                        StatisticsRenderer.this.bytesReceived = bytesReceived;
                        lastBandwidthUpdate = LocalDateTime.now();

                        updateBandwidthUi(downloadRate, uploadRate);
                    }
                }
            }
        }
    }

    private void updateBandwidthUi(BigInteger downloadRate, BigInteger uploadRate) {
        Log.i(TAG, "Download: " + downloadRate + "kbps, Upload: " + uploadRate + " kbps");
        //runOnUiThread because only the original thread that created a view hierarchy can touch its views
        activity.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                binding.bandwidth.setText(activity.getString(R.string.bandwidth, downloadRate, uploadRate));
            }
        });
    }
}
