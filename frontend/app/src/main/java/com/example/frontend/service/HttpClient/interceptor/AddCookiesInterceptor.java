package com.example.frontend.service.HttpClient.interceptor;
// Original written by tsuharesu
// Adapted to create a "drop it in and watch it work" approach by Nikhil Jha.
// Just add your package statement and drop it in the folder with all your other classes.

import android.content.Context;
import android.preference.PreferenceManager;
import android.util.Log;

import java.io.IOException;
import java.util.HashSet;

import okhttp3.Interceptor;
import okhttp3.Request;
import okhttp3.Response;

/**
 * This interceptor put all the Cookies in Preferences in the Request.
 * Your implementation on how to get the Preferences may ary, but this will work 99% of the time.
 */
public class AddCookiesInterceptor implements Interceptor {
    public static final String PREF_COOKIES = "PREF_COOKIES";
    // We're storing our stuff in a database made just for cookies called PREF_COOKIES.
    // I reccomend you do this, and don't change this default value.
    private Context context;

    public AddCookiesInterceptor(Context context) {
        this.context = context;
    }

    @Override
    public Response intercept(Interceptor.Chain chain) throws IOException {
        Request.Builder builder = chain.request().newBuilder();

        // Add cookie from shared preferences if they are stored
       if (PreferenceManager.getDefaultSharedPreferences(context).contains(PREF_COOKIES)) {
           HashSet<String> preferences = (HashSet<String>) PreferenceManager.getDefaultSharedPreferences(context).getStringSet(PREF_COOKIES, new HashSet<String>());
           for (String cookie : preferences) {
               builder.addHeader("Cookie", cookie);
           }

           Log.i(this.getClass().getName(), "Successfully added cookies to request");
       } else {
           Log.i(this.getClass().getName(), "No stored cookies found");
       }

       // continue the request
        Request request = builder.build();
        Response response = chain.proceed(request);
        return response;
    }
}