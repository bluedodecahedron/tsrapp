package com.example.frontend.service.client.interceptor;
// Original written by tsuharesu
// Adapted to create a "drop it in and watch it work" approach by Nikhil Jha.
// Just add your package statement and drop it in the folder with all your other classes.

import android.content.Context;
import android.content.SharedPreferences;
import android.preference.PreferenceManager;
import android.util.Log;

import org.apache.commons.lang3.StringUtils;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashSet;

import okhttp3.Interceptor;
import okhttp3.Response;

public class ReceivedCookiesInterceptor implements Interceptor {
    private Context context;
    public ReceivedCookiesInterceptor(Context context) {
        this.context = context;
    } // AddCookiesInterceptor()
    @Override
    public Response intercept(Chain chain) throws IOException {
        Response originalResponse = chain.proceed(chain.request());

        if (!originalResponse.headers("Set-Cookie").isEmpty()) {
            HashSet<String> storageCookies = (HashSet<String>) PreferenceManager.getDefaultSharedPreferences(context).getStringSet("PREF_COOKIES", new HashSet<String>());

            ArrayList<String> responseCookies = new ArrayList<>();
            for (String header : originalResponse.headers("Set-Cookie")) {
                responseCookies.add(header.split(";")[0]);
            }
            String cookie = StringUtils.join(responseCookies, "; ");
            storageCookies.add(cookie);

            SharedPreferences.Editor memes = PreferenceManager.getDefaultSharedPreferences(context).edit();
            memes.putStringSet("PREF_COOKIES", storageCookies).apply();
            memes.commit();

            Log.i(this.getClass().getName(), "Successfully stored cookies in database");
        } else {
            Log.e(this.getClass().getName(), "No cookies found in request");
        }
        return originalResponse;
    }
}