-- Get sender, recipient and content for each message
select sender.username as "sender",
    recipient.username as "recipient",
    message.content,
    message.time_sent
from user sender
inner join conversation
    on sender.id = conversation.sender_id
inner join message
    on message.id = conversation.message_id
inner join user recipient
    on recipient.id = conversation.recipient_id;


-- Get IDs of all people who have you a message
select distinct conversation.sender_id
from conversation
inner join user
    on user.id = conversation.recipient_id
where user.id != conversation.sender_id;


-- Get only most recent message record for each person who has sent you a message
select message.content, max(message.time_sent)
from message
inner join conversation
where message.id = conversation.message_id
    and conversation.sender_id != 1 -- 1 is the input sender_id
group by conversation.sender_id;
