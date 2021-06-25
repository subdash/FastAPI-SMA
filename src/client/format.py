from datetime import datetime
from typing import List


def fmt_conversation(conversation: List[dict]) -> str:
    """
    Format a list of messages for user-friendly display.

    :param conversation: A list of dictionaries with message content, recipient
    name, sender name and the time sent
    :return: A string to be printed to the console representing a conversation
    or previews of multiple conversations
    """
    assert isinstance(conversation, list)
    assert len(conversation) > 0
    assert isinstance(conversation[0], dict)
    assert {"content", "recipient", "sender", "time_sent"} == conversation[0].keys()

    ret_str = ""
    for message in conversation:
        ts = datetime.fromisoformat(message['time_sent'])
        am_pm = "am" if ts.hour < 13 else "pm"
        hour = ts.hour if ts.hour < 13 else ts.hour - 12
        minute = ts.strftime("%M")
        timestamp = f"{hour}:{minute}{am_pm}, {ts.month}/{ts.day}/{ts.year}"

        ret_str += f"<{message['sender']}> at {timestamp}:\n"
        ret_str += f"\t{message['content']}\n\n"

    return ret_str
