import re
import json
from PatternSpider.utils.dict_utils import DictUtils


def parse_attache(attachment):
    if type(attachment) == list:
        attachment = attachment[0]
    attach_list = []
    if attachment:
        if "all_subattachments" in attachment:
            nodes = attachment["all_subattachments"]["nodes"]
            for attach in nodes:
                typename = attach["media"]["__typename"]
                uri = dict_util.get_data_from_field(attach, 'uri')
                caption = dict_util.get_data_from_field(attach, 'accessibility_caption')
                attach_list.append({
                    "typename": typename,
                    "uri": uri.replace('\\', '') if uri else '',
                    "caption": caption if caption else ''
                })
        if "media" in attachment:
            typename = attachment["media"]["__typename"]
            if typename == "Photo":
                uri = dict_util.get_data_from_field(attachment, 'uri')
                caption = dict_util.get_data_from_field(attachment, 'accessibility_caption')
                attach_list.append({
                    "typename": typename,
                    "uri": uri.replace('\\', '') if uri else '',
                    "caption": caption if caption else ''
                })
            elif typename == "Video":
                uri = dict_util.get_data_from_field(attachment, 'playable_url')
                thumbnail = dict_util.get_data_from_field(attachment, 'uri')
                publish_time = dict_util.get_data_from_field(attachment, 'publish_time')
                duration = dict_util.get_data_from_field(attachment, 'playable_duration_in_ms')
                attach_list.append({
                    "typename": typename,
                    "uri": uri.replace('\\', '') if uri else '',
                    "caption": '',
                    "thumbnail": thumbnail.replace('\\', '') if thumbnail else '',
                    "publish_time": publish_time if publish_time else '',
                    "duration": duration if duration else ''
                })
            elif typename == 'Sticker':
                uri = dict_util.get_data_from_field(attachment, 'uri')
                caption = dict_util.get_data_from_field(attachment, 'name')
                attach_list.append({
                    "typename": typename,
                    "uri": uri.replace('\\', '') if uri else '',
                    "caption": caption if caption else ''
                })
                pass

    return attach_list


dict_util = DictUtils()

with open('page_source', 'r', encoding='utf-8') as f:
    page_source = f.read()
over_datas = []

bboxes = re.findall('\{"__bbox":\{.*?extra_context.*?\}\}', page_source)
if bboxes:
    bboxes_dicts = [json.loads(box) for box in bboxes]
    for bboxes_dict in bboxes_dicts:
        display_comments = dict_util.get_data_from_field(bboxes_dict, 'display_comments')
        if not display_comments:
            continue
        comments = display_comments['edges']
        for comment in comments:
            node = comment['node']
            print(node)
            user = node['author']
            attachment = dict_util.get_data_from_field(node['attachments'], 'attachment')
            attach_list = parse_attache(attachment) if attachment else ""
            content = node['body']['text'] if node['body'] else ""
            node.update({
                "comment_id": node['legacy_fbid'],
                "post_id": "",
                "post_url": "",
                "userid": user['id'],
                "homepage": user['url'],
                "content": content,
                "content_cn": "",
                "comment_attach": json.dumps(attach_list) if attach_list else "",
                "local_attach": "",
                "comment_time": node['created_time'],
            })
            over_datas.append(node)

print(over_datas)
