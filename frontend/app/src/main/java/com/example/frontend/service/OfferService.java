package com.example.frontend.service;

import android.content.Context;
import android.content.SharedPreferences;
import android.preference.PreferenceManager;
import android.util.Log;

import com.example.frontend.schema.Offer;
import com.example.frontend.service.HttpClient.API;
import com.example.frontend.service.HttpClient.RetrofitClient;
import com.example.frontend.util.NetworkMeasures;

import java.util.HashSet;
import java.util.function.Consumer;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class OfferService {
    Context context;
    Consumer<Response<Offer>> onOfferSuccess;
    Consumer<Response<Offer>> onOfferFailure;
    Consumer<Throwable> onRequestFailure;

    public OfferService(
            Context context,
            Consumer<Response<Offer>> onOfferSuccess,
            Consumer<Response<Offer>> onOfferFailure,
            Consumer<Throwable> onRequestFailure
    ) {
        this.context = context;
        this.onOfferSuccess = onOfferSuccess;
        this.onOfferFailure = onOfferFailure;
        this.onRequestFailure = onRequestFailure;
    }

    public void offer(Offer offer) {
        //get request call
        API api = RetrofitClient.getInstance(context).getAPI();
        Call<Offer> call = api.offer(offer);

        //queue request (is handled asynchronously)
        call.enqueue(new OfferCallback(offer));
    }

    class OfferCallback implements Callback<Offer> {
        Offer offer;

        public OfferCallback(Offer offer) {
            super();
            this.offer = offer;
        }

        @Override
        public void onResponse(Call<Offer> call, Response<Offer> response) {
            if(response.isSuccessful()) {
                handleOfferSuccess(offer, response);
                onOfferSuccess.accept(response);
            } else {
                handleOfferFailure(offer, response);
                onOfferFailure.accept(response);
            }
        }

        @Override
        public void onFailure(Call<Offer> call, Throwable t) {
            handleRequestFailure(t);
            onRequestFailure.accept(t);
        }
    }

    private void handleOfferSuccess(Offer offer, Response<Offer> response) {
        Log.i(this.getClass().getName(), "Offer successful, response time: " + NetworkMeasures.getResponseTime(response) + "ms");
    }

    private void handleOfferFailure(Offer offer, Response<Offer> response) {
        Log.e(this.getClass().getName(), "Offer request for " + offer + " failed with status code " + response.code() + ": " + response.message());
    }

    private void handleRequestFailure(Throwable t) {
        Log.e(this.getClass().getName(), "Request failed. Bad connection?");
        t.printStackTrace();
    }
}
