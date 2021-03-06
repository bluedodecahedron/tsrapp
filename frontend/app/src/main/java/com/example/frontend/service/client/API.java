package com.example.frontend.service.client;

import com.example.frontend.schema.UserSchema;

import okhttp3.MultipartBody;
import okhttp3.ResponseBody;
import retrofit2.Call;
import retrofit2.http.Body;
import retrofit2.http.Multipart;
import retrofit2.http.POST;
import retrofit2.http.Part;

public interface API {
    @POST("api/authentication/login")
    Call<ResponseBody> login(@Body UserSchema userSchema);

    @Multipart
    @POST("api/tsdr/trafficimg")
    Call<ResponseBody> trafficSignDetection(@Part MultipartBody.Part imageFile);

    @POST("api/tsdr/test")
    Call<ResponseBody> test();
}