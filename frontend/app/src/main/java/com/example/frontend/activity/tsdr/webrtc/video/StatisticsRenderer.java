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
import java.util.TimerTask;

public class StatisticsRenderer extends TimerTask {
    private BigInteger bytesSent = BigInteger.ZERO;
    private BigInteger bytesReceived = BigInteger.ZERO;
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

    @Override
    public void run() {
        update();
    }

    public void update() {
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
        Log.i(TAG, "PeerConnection Stats Report: \n" + rtcStatsReport);
        BigInteger downloadRate = BigInteger.ZERO;
        BigInteger uploadRate = BigInteger.ZERO;
        Long outboundFrameWidth = 0L;
        Long outboundFrameHeight = 0L;
        Long inboundFrameWidth = 0L;
        Long inboundFrameHeight = 0L;
        Double outboundFramesPerSecond = 0D;
        Double inboundFramesPerSecond = 0D;
        String outboundQualityLimitationReason = "";

        long updateDelay = ChronoUnit.MILLIS.between(lastBandwidthUpdate, LocalDateTime.now());
        lastBandwidthUpdate = LocalDateTime.now();

        Map<String, RTCStats> statsmap = rtcStatsReport.getStatsMap();
        for(RTCStats rtcStats : statsmap.values()) {
            if (rtcStats.getType().equals("inbound-rtp")) {
                Log.i(TAG, "Inbound-RTP Stats: " + rtcStats);

                Map<String, Object> members = rtcStats.getMembers();
                BigInteger bytesReceived = (BigInteger) members.get("bytesReceived");
                if(bytesReceived != null) {
                    BigInteger bytesReceivedDiff = bytesReceived.subtract(StatisticsRenderer.this.bytesReceived);
                    //dividing bytes by milliseconds is the same as dividing kilobytes by seconds
                    downloadRate = bytesReceivedDiff.divide(BigInteger.valueOf(updateDelay));

                    StatisticsRenderer.this.bytesReceived = bytesReceived;
                }
                Long frameWidth = (Long) members.get("frameWidth");
                Long frameHeight = (Long) members.get("frameHeight");
                Double framesPerSecond = (Double) members.get("framesPerSecond");
                if(frameWidth != null || frameHeight != null) {
                    inboundFrameWidth = frameWidth;
                    inboundFrameHeight = frameHeight;
                    inboundFramesPerSecond = framesPerSecond;
                }
            }

            if (rtcStats.getType().equals("outbound-rtp")) {
                Log.i(TAG, "Outbound-RTP Stats: " + rtcStats);

                Map<String, Object> members = rtcStats.getMembers();
                BigInteger bytesSent = (BigInteger) members.get("bytesSent");
                if(bytesSent != null) {
                    BigInteger bytesSentDiff = bytesSent.subtract(StatisticsRenderer.this.bytesSent);
                    //dividing bytes by milliseconds is the same as dividing kilobytes by seconds
                    uploadRate = bytesSentDiff.divide(BigInteger.valueOf(updateDelay));

                    StatisticsRenderer.this.bytesSent = bytesSent;
                }
                Long frameWidth = (Long) members.get("frameWidth");
                Long frameHeight = (Long) members.get("frameHeight");
                Double framesPerSecond = (Double) members.get("framesPerSecond");
                String qualityLimitationReason = (String) members.get("qualityLimitationReason");
                if(frameWidth != null || frameHeight != null) {
                    outboundFrameWidth = frameWidth;
                    outboundFrameHeight = frameHeight;
                    outboundFramesPerSecond = framesPerSecond;
                    outboundQualityLimitationReason = qualityLimitationReason;
                }
            }
        }

        updateUi(downloadRate, uploadRate, outboundFrameWidth, outboundFrameHeight, inboundFrameWidth, inboundFrameHeight, outboundFramesPerSecond, inboundFramesPerSecond, outboundQualityLimitationReason);
    }

    private void updateUi(BigInteger downloadRate, BigInteger uploadRate, Long outboundFrameWidth, Long outboundFrameHeight, Long inboundFrameWidth, Long inboundFrameHeight, Double outboundFramesPerSecond, Double inboundFramesPerSecond, String outboundQualityLimitationReason) {
        Log.i(TAG, "Download: " + downloadRate + "kbps, Upload: " + uploadRate + " kbps");
        //runOnUiThread because only the original thread that created a view hierarchy can touch its views
        activity.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                binding.bandwidth.setText(activity.getString(
                        R.string.bandwidth,
                        uploadRate,
                        outboundFramesPerSecond.toString(),
                        downloadRate,
                        inboundFramesPerSecond.toString()
                ));
                binding.frameSize.setText(activity.getString(
                        R.string.frameSize,
                        outboundFrameWidth.toString(),
                        outboundFrameHeight.toString(),
                        inboundFrameWidth.toString(),
                        inboundFrameHeight.toString()
                ));
                binding.qualityLimitationReason.setText(activity.getString(
                        R.string.qualityLimitationReason,
                        outboundQualityLimitationReason
                ));
            }
        });
    }
}
