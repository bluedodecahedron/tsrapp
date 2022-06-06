package com.example.frontend.activity;

import android.content.Context;
import android.content.ContextWrapper;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.ImageFormat;
import android.graphics.Rect;
import android.graphics.YuvImage;
import android.media.Image;
import android.os.Bundle;
import android.util.Log;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;
import androidx.camera.core.CameraSelector;
import androidx.camera.core.ExperimentalGetImage;
import androidx.camera.core.ImageAnalysis;
import androidx.camera.core.ImageProxy;
import androidx.camera.core.Preview;
import androidx.camera.lifecycle.ProcessCameraProvider;
import androidx.camera.view.PreviewView;
import androidx.core.content.ContextCompat;
import androidx.lifecycle.LifecycleOwner;

import com.example.frontend.R;
import com.example.frontend.service.TsdrService;
import com.example.frontend.service.client.API;
import com.example.frontend.service.client.RetrofitClient;
import com.example.frontend.util.NetworkMeasures;
import com.google.common.util.concurrent.ListenableFuture;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.Objects;
import java.util.concurrent.ExecutionException;

import okhttp3.MediaType;
import okhttp3.MultipartBody;
import okhttp3.RequestBody;
import okhttp3.ResponseBody;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

@ExperimentalGetImage
public class CameraActivity extends AppCompatActivity {
    private PreviewView previewView;
    private ListenableFuture<ProcessCameraProvider> cameraProviderFuture;
    private TextView textView;

    private LocalDateTime latestAnalysisTime = LocalDateTime.now();
    private TsdrService tsdrService;

    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_camera);

        // get new tsdr service
        tsdrService = new TsdrService(
                this,
                this::onTsdrSuccess,
                this::onTsdrFailure,
                this::onRequestFailure
        );

        // initialize camera
        previewView = findViewById(R.id.previewView);
        cameraProviderFuture = ProcessCameraProvider.getInstance(this);
        textView = findViewById(R.id.orientation);
        cameraProviderFuture.addListener(new Runnable() {
            @Override
            public void run() {
                try {
                    ProcessCameraProvider cameraProvider = cameraProviderFuture.get();
                    bindImageAnalysis(cameraProvider);
                } catch (ExecutionException | InterruptedException e) {
                    e.printStackTrace();
                }
            }
        }, ContextCompat.getMainExecutor(this));
    }

    private void bindImageAnalysis(@NonNull ProcessCameraProvider cameraProvider) {
        ImageAnalysis imageAnalysis =
                new ImageAnalysis
                        .Builder()
                        //.setTargetResolution(new Size(640, 480))
                        .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
                        .build();
        imageAnalysis.setAnalyzer(ContextCompat.getMainExecutor(this), new TsdrAnalyzer());

        Preview preview = new Preview.Builder().build();
        CameraSelector cameraSelector = new CameraSelector.Builder()
                .requireLensFacing(CameraSelector.LENS_FACING_BACK).build();
        preview.setSurfaceProvider(previewView.getSurfaceProvider());
        cameraProvider.bindToLifecycle((LifecycleOwner)this, cameraSelector,
                imageAnalysis, preview);
    }

    class TsdrAnalyzer implements ImageAnalysis.Analyzer {
        @Override
        public void analyze(@NonNull ImageProxy imageProxy) {
            // analyze image every 2 seconds (temporary solution)
            long timeDiff = ChronoUnit.MILLIS.between(latestAnalysisTime, LocalDateTime.now());
            if (timeDiff > 2000L) {
                Log.i(this.getClass().getName(), "Analyzing new image");
                latestAnalysisTime = LocalDateTime.now();
                tsdrService.trafficSignDetection(imageProxy);
            }
            imageProxy.close();
        }
    }

    private void onTsdrSuccess(Response<ResponseBody> response) {
        Toast.makeText(this, "TSDR success, response time: " + NetworkMeasures.getResponseTime(response) + "ms", Toast.LENGTH_SHORT).show();
    }

    private void onTsdrFailure(Response<ResponseBody> response) {
        Toast.makeText(this, "TSDR failed: " + response.message(), Toast.LENGTH_SHORT).show();
    }

    private void onRequestFailure(Throwable t) {
        Toast.makeText(this, "Request failed. Bad connection?", Toast.LENGTH_SHORT).show();
    }

}