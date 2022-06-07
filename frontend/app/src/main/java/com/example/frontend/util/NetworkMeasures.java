package com.example.frontend.util;

import okhttp3.ResponseBody;
import retrofit2.Response;

public class NetworkMeasures {
    public static long getResponseTime(Response<ResponseBody> response) {
        long requestTime = response.raw().sentRequestAtMillis();
        long responseTime = response.raw().receivedResponseAtMillis();
        //time taken to receive the response after the request was sent
        return  responseTime - requestTime;
    }
}
