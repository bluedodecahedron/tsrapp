package com.example.frontend.service;

import android.content.Context;
import android.content.ContextWrapper;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.ImageFormat;
import android.graphics.Rect;
import android.graphics.YuvImage;
import android.media.Image;
import android.util.Log;
import android.widget.Toast;

import androidx.camera.core.ExperimentalGetImage;
import androidx.camera.core.ImageProxy;

import com.example.frontend.service.client.API;
import com.example.frontend.service.client.RetrofitClient;
import com.example.frontend.util.ImageConversion;
import com.example.frontend.util.NetworkMeasures;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.util.Objects;
import java.util.function.Consumer;

import okhttp3.MediaType;
import okhttp3.MultipartBody;
import okhttp3.RequestBody;
import okhttp3.ResponseBody;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

@ExperimentalGetImage
public class TsdrService {
    Context context;
    Consumer<Response<ResponseBody>> onTsdrSuccess;
    Consumer<Response<ResponseBody>> onTsdrFailure;
    Consumer<Throwable> onRequestFailure;

    public TsdrService(
            Context context,
            Consumer<Response<ResponseBody>> onTsdrSuccess,
            Consumer<Response<ResponseBody>> onTsdrFailure,
            Consumer<Throwable> onRequestFailure
            ) {
        this.context = context;
        this.onTsdrSuccess = onTsdrSuccess;
        this.onTsdrFailure = onTsdrFailure;
        this.onRequestFailure = onRequestFailure;
    }

    // Upload the image to the remote database
    public void trafficSignDetection(ImageProxy imageProxy) {
        Objects.requireNonNull(imageProxy);

        // convert image
        ImageConversion imageConversion = new ImageConversion(context);
        MultipartBody.Part formData = imageConversion.toFormData(imageProxy);

        // get request call
        API api = RetrofitClient.getInstance(context).getAPI();
        Call<ResponseBody> call = api.trafficSignDetection(formData);

        //queue request (is handled asynchronously)
        call.enqueue(new TsdrCallback());
    }

    class TsdrCallback implements Callback<ResponseBody> {
        @Override
        public void onResponse(Call<ResponseBody> call, Response<ResponseBody> response) {
            if (response.isSuccessful()) {
                handleTsdrSuccess(response);
                onTsdrSuccess.accept(response);
            } else {
                handleTsdrFailure(response);
                onTsdrFailure.accept(response);
            }
        }

        @Override
        public void onFailure(Call<ResponseBody> call, Throwable t) {
            handleRequestFailure(t);
            onRequestFailure.accept(t);
        }
    }

    private void handleTsdrSuccess(Response<ResponseBody> response) {
        Log.i(this.getClass().getName(), "Successful image upload");
        Log.i(this.getClass().getName(), "Response time: " + NetworkMeasures.getResponseTime(response) + "ms");
    }

    private void handleTsdrFailure(Response<ResponseBody> response) {
        Log.e(this.getClass().getName(), "TSDR Request failed with status code " + response.code() + ": " + response.message());
    }

    private void handleRequestFailure(Throwable t) {
        Log.e(this.getClass().getName(), "Request failed. Bad connection?");
        t.printStackTrace();
    }
}
