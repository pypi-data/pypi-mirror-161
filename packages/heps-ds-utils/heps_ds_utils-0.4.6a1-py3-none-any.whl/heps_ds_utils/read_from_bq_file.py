"""_summary_

Returns:
    _type_: _description_
"""

import re


def bq_command_parser(bq_file):
    """Function to Read BigQuery .bq files and convert them into a list of BigQuery Commands.
    Args:
        bq_file (_type_): Complete Path of the BigQuery File

    Returns:
        _type_: list of BigQuery Commands
    """
    with open(bq_file, "r", encoding="utf-8") as file:
        text = file.readlines()

    # First concat all list elements to get one string
    text = "".join(text)

    # Secondly, remove block comment
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)

    # Thirdly, remove line comments that are we are sure with
    # Note that comments that contain ' or " may remains after this filter
    text = re.sub(r"^\-\-.*", "\n", text, flags=re.M)
    text = re.sub(r"\-\-(?!(.*\'|.*\")).*\n", "\n", text, flags=re.M)

    previous_text = ""
    while previous_text != text:
        previous_text = text
        
        # Find string that are specified with ' or " and contains --
        # Those strings' locations are stored in string_spans list
        # From string_spans find dangerous ones and stored dangerous_spans
        string_spans = []
        dangerous_spans = []
        for find in re.finditer("(('|\").*?[\-]+.*?('|\"))", text, flags=re.M):
            control_start = string_spans[-1][-1] if string_spans != [] else 0
            if not re.search(r'\-\-', text[control_start:find.start()]) or \
                re.search(r'\n', text[control_start:find.start()]):
                dangerous_spans.append((find.start(), find.end()))
            string_spans.append((find.start(), find.end()))
        
        # Now find comments contains string specification like in the following:
        # --comment_1 'string
        # And check that those findings are located in dangerous spans
        # if not add to slice spans
        slice_spans = []
        for find in re.finditer(r"\-{2,}(?!.*\-\-).*", text, flags=re.M):
            safe = True
            for span in dangerous_spans:
                if find.start() >= span[0] and find.start() <= span[1]:
                    safe = False
                    break
            if safe:
                slice_spans.append((find.start(), find.end()))

        # By looking reverse of slice spans remove commented findings
        # The reason reverse list is using is if you use it ordered the location would be changed
        for start, end in reversed(slice_spans):
            text = text[:start] + text[end:]

    text = re.sub(r"(\n|\s|\t)+", " ", text)
    # add ; to last query if it doesnt have it
    if text[0] != ";":
        text = text + ";"
    # return [query.strip() for query in text.split(';')][:-1]
    return [query.strip() for query in text.split(";") if query.strip() != ""]