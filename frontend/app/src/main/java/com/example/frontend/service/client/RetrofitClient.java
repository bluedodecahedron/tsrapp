package com.example.frontend.service.client;

import android.content.Context;
import android.content.res.Resources;
import android.util.Log;

import com.example.frontend.R;
import com.example.frontend.service.client.interceptor.AddCookiesInterceptor;
import com.example.frontend.service.client.interceptor.ReceivedCookiesInterceptor;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;

import okhttp3.OkHttpClient;
import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;

public class RetrofitClient {
    private String backendHost = "localhost:8080";
    private final String baseUrl;

    private static RetrofitClient mInstance;
    private final Retrofit retrofit;

    private RetrofitClient(Context context) {
        OkHttpClient client = new OkHttpClient();
        OkHttpClient.Builder builder = new OkHttpClient.Builder();

        loadBackendHost(context);
        baseUrl = String.format("http://%s/", backendHost);

        // Cookie loading before each request
        builder.addInterceptor(new AddCookiesInterceptor(context));
        // Cookie saving after each request
        builder.addInterceptor(new ReceivedCookiesInterceptor(context));
        client = builder.build();

        retrofit = new Retrofit.Builder()
                .baseUrl(baseUrl)
                .client(client)
                .addConverterFactory(GsonConverterFactory.create())
                .build();
    }

    private void loadBackendHost(Context context) {
        try {
            InputStream inputStream = context.getResources().openRawResource(R.raw.backend_host);
            String firstLine = new BufferedReader(new InputStreamReader(inputStream)).readLine();
            if(!firstLine.isEmpty()) {
                backendHost = firstLine;
                Log.i(this.getClass().getName(), "Loaded backend host: '" + backendHost + "'");
            } else {
                Log.i(this.getClass().getName(), "Backend host file was empty. Use default host: " + backendHost);
            }
        } catch (Resources.NotFoundException e) {
            Log.i(this.getClass().getName(), "No backend host file found. Use default host: " + backendHost);
        } catch (IOException e) {
            throw new RuntimeException("Could not read from backend host file", e);
        }
    }

    public static synchronized RetrofitClient getInstance(Context context) {
        if (mInstance == null) {
            mInstance = new RetrofitClient(context);
        }
        return mInstance;
    }

    public API getAPI() {
        return retrofit.create(API.class);
    }
}