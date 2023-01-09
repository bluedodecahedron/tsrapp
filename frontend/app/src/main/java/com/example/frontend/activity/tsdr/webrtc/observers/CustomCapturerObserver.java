package com.example.frontend.activity.tsdr.webrtc.observers;

import org.webrtc.CapturerObserver;
import org.webrtc.VideoFrame;

import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;

public class CustomCapturerObserver implements CapturerObserver {
    private final CapturerObserver capturerObserver;
    private LocalDateTime lastFrameTime;
    private static final int MAX_FPS = 10; //Limits FPS to some custom value since device video capturer is usually restricted to fixed values (often 15, 30, 45, 60)

    public CustomCapturerObserver(CapturerObserver capturerObserver) {
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
        long fpsDelta = 1000L/ MAX_FPS - 10L;
        LocalDateTime nextFrameTime = lastFrameTime.plus(fpsDelta, ChronoUnit.MILLIS);
        if (LocalDateTime.now().isAfter(nextFrameTime)) {
            lastFrameTime = LocalDateTime.now();
            capturerObserver.onFrameCaptured(videoFrame);
        } else {
            //drop frame
        }
    }
}