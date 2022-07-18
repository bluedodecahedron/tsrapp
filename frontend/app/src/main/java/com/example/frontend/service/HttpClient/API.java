package com.example.frontend.service.HttpClient;

import com.example.frontend.schema.Offer;
import com.example.frontend.schema.User;

import okhttp3.MultipartBody;
import okhttp3.ResponseBody;
import retrofit2.Call;
import retrofit2.http.Body;
import retrofit2.http.Multipart;
import retrofit2.http.POST;
import retrofit2.http.Part;
import retrofit2.http.Path;

public interface API {
    @POST("api/authentication/login")
    Call<ResponseBody> login(@Body User user);

    @Multipart
    @POST("api/tsdr/trafficimg/{id}")
    Call<ResponseBody> trafficSignDetection(@Path("id") int groupId, @Part MultipartBody.Part imageFile);

    @POST("api/tsdr/test")
    Call<ResponseBody> test();

    @POST("/api/webrtc/server/offer")
    Call<Offer> offer(@Body Offer offer);
}