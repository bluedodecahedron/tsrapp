package com.example.frontend.activity.tsdr.http;

import android.os.Bundle;
import android.util.Log;
import android.widget.TextView;

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
import com.google.common.util.concurrent.ListenableFuture;

import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.concurrent.ExecutionException;

import okhttp3.ResponseBody;
import retrofit2.Response;

@ExperimentalGetImage
public class HttpActivity extends AppCompatActivity {
    private PreviewView previewView;
    private ListenableFuture<ProcessCameraProvider> cameraProviderFuture;
    private TextView textView;

    private LocalDateTime latestAnalysisTime = LocalDateTime.now();
    private TsdrService tsdrService;

    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_http);

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
                        .setBackpressureStrategy(ImageAnalysis.STRATEGY_BLOCK_PRODUCER)
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
            if (timeDiff > 100L) {
                Log.i(this.getClass().getName(), "Analyzing new image");
                latestAnalysisTime = LocalDateTime.now();
                tsdrService.trafficSignDetection(imageProxy);
            }
            imageProxy.close();
        }
    }

    private void onTsdrSuccess(Response<ResponseBody> response) {
        //Toast.makeText(this, "TSDR success, response time: " + NetworkMeasures.getResponseTime(response) + "ms", Toast.LENGTH_SHORT).show();
    }

    private void onTsdrFailure(Response<ResponseBody> response) {
        //Toast.makeText(this, "TSDR failed: " + response.message(), Toast.LENGTH_SHORT).show();
    }

    private void onRequestFailure(Throwable t) {
        //Toast.makeText(this, "Request failed. Bad connection?", Toast.LENGTH_SHORT).show();
    }

}