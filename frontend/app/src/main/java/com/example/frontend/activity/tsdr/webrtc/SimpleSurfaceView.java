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
    private static final int UPDATE_DELAY = 1000;
    private LocalDateTime lastUpdateTime = LocalDateTime.now();
    private int frame_counter = 0;
    private Consumer<Float> updateFpsUi;
    private Runnable updateBandwithUi;
    private String TAG;

    public SimpleSurfaceView(Context context) {
        super(context);
    }

    public SimpleSurfaceView(Context context, AttributeSet attrs) {
        super(context, attrs);
    }

    @Override
    public void onFrame(VideoFrame frame) {
        //Log.d(TAG, "New SurfaceView frame");
        if(this.updateFpsUi != null && this.TAG != null) {
            frame_counter++;
            if(ChronoUnit.MILLIS.between(lastUpdateTime, LocalDateTime.now()) > UPDATE_DELAY) {
                updateFpsCounter();
                frame_counter = 0;
            }
        }
        super.onFrame(frame);
    }

    public void setUpdateFpsUi(Consumer<Float> updateFpsUi) {
        this.updateFpsUi = updateFpsUi;
    }

    public void setUpdateBandwithUi(Runnable updateBandwithUi) {
        this.updateBandwithUi = updateBandwithUi;
    }

    public void setTAG(String TAG) {
        this.TAG = TAG;
    }

    private void updateFpsCounter() {
        Float delay = ChronoUnit.MILLIS.between(lastUpdateTime, LocalDateTime.now()) / 1000.0F;
        Float fps = frame_counter / delay;
        lastUpdateTime = LocalDateTime.now();
        updateFpsUi.accept(fps);
        updateBandwithUi.run();
    }
}
