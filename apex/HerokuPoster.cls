public class HerokuPoster {
    
    @future(callout=true)
    public static void doPost(String sobjectsJson) {
        HttpRequest req = new HttpRequest();
        req.setMethod('POST');
        req.setEndpoint('https://my-app-name.herokuapp.com/sf-data');
        req.setBody(sobjectsJson);
        req.setHeader('Content-Type', 'application/json');
        
        Http http = new Http();
        HttpResponse response = http.send(req);
    }
}

