'use strict'

const fs=require('fs');
var testApp = angular.module('testApp', []);

testApp.controller('testController' , function ($scope, $http) {
    //$scope.home = "This is the homepage";
    

    //alert($scope.username);
    
    $scope.createJson = function () {
    
        
    let patient = {
        name: $scope.name,
        email: $scope.email,
        gender: $scope.gender,
        claim_data: $scope.message
    };
    
    let data = JSON.stringify(patient);

    fs.writeFileSync('ex.json',data,finished);
    /*
        var data={
        "$class": "org.acme.mynetwork.Cleaner",
  "cleanerID": $scope.username,
  "TID": " "


       }
        $http.post("http://localhost:3000/api/org.acme.mynetwork.Cleaner", data)
            .then(function successCallback(response){
                alert("Successfully POST-ed data");
            }, function errorCallback(response){
                alert("POST-ing of data failed");
            });   
    */
        };
    function finished(err)
    {
        console.log('success');
    }
    
});