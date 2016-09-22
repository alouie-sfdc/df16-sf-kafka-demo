trigger FeedCommentSendToHerokuTrigger on FeedComment (after insert) {
    if (Trigger.isInsert) {
        HerokuPoster.doPost(JSON.serialize(Trigger.new));
    }
}

