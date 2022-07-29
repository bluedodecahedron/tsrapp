package com.example.frontend.activity.tsdr.webrtc;

import android.content.Context;
import android.util.AttributeSet;
import android.util.Log;

import org.webrtc.SurfaceViewRenderer;
import org.webrtc.VideoFrame;

import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.function.Consumer;

public class SimpleSurfaceView extends SurfaceViewRenderer {
    private LocalDateTime lastFrameTime = LocalDateTime.now();
    private Consumer<Float> updateFpsUi;
    private String TAG;

    public SimpleSurfaceView(Context context) {
        super(context);
    }

    public SimpleSurfaceView(Context context, AttributeSet attrs) {
        super(context, attrs);
    }

    @Override
    public void onFrame(VideoFrame frame) {
        Log.d(TAG, "New SurfaceView frame");
        if(this.updateFpsUi != null && this.TAG != null) {
            updateFpsCounter();
        }
        super.onFrame(frame);
    }

    public void setUpdateFpsUi(Consumer<Float> updateFpsUi) {
        this.updateFpsUi = updateFpsUi;
    }

    public void setTAG(String TAG) {
        this.TAG = TAG;
    }

    private void updateFpsCounter() {
        Float fps = 1000.0F/ ChronoUnit.MILLIS.between(lastFrameTime, LocalDateTime.now());
        lastFrameTime = LocalDateTime.now();
        updateFpsUi.accept(fps);
    }
}
