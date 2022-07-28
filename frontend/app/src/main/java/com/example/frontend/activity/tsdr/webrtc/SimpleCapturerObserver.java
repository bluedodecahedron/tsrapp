package com.example.frontend.activity.tsdr.webrtc;

import org.webrtc.CapturerObserver;
import org.webrtc.VideoFrame;

import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;

public class SimpleCapturerObserver implements CapturerObserver {
    private final CapturerObserver capturerObserver;
    private LocalDateTime lastFrameTime;
    private static final int MAXFPS = 10;

    public SimpleCapturerObserver(CapturerObserver capturerObserver) {
        this.capturerObserver = capturerObserver;
        this.lastFrameTime = LocalDateTime.now();

    }

    @Override
    public void onCapturerStarted(boolean b) {
        capturerObserver.onCapturerStarted(b);
    }

    @Override
    public void onCapturerStopped() {
        capturerObserver.onCapturerStopped();
    }

    @Override
    public void onFrameCaptured(VideoFrame videoFrame) {
        long fpsDelta = 1000L/MAXFPS - 10L;
        LocalDateTime nextFrameTime = lastFrameTime.plus(fpsDelta, ChronoUnit.MILLIS);
        if (LocalDateTime.now().isAfter(nextFrameTime)) {
            lastFrameTime = LocalDateTime.now();
            capturerObserver.onFrameCaptured(videoFrame);
        } else {
            //drop frame
        }
    }
}