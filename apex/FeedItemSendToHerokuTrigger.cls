trigger FeedItemSendToHerokuTrigger on FeedItem (after insert) {
    if (Trigger.isInsert) {
        HerokuPoster.doPost(JSON.serialize(Trigger.new));
    }
}

