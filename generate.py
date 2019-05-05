import requests
from csv import DictReader
from io import StringIO
from collections import defaultdict

CANDIDATE_URL='https://candidates.democracyclub.org.uk/media/candidates-europarl.2019-05-23.csv'

def download_data():
    req = requests.get(CANDIDATE_URL)

    # avoid: "_csv.Error: new-line character seen in unquoted field - do you
    # need to open the file in universal-newline mode?"
    stream = StringIO(req.text, newline='')

    csvdata = DictReader(stream)
    return csvdata

def group_data_by_party_region(data):
    buckets = defaultdict(list)

    for row in data:
        key = (row['party_name'], row['post_label'])
        buckets[key].append(row)

    for candidate_list in buckets.values():
        candidate_list.sort(key=lambda row: int(row['party_list_position'] or '1'))

    return buckets

def get_data():
    data = download_data()
    return group_data_by_party_region(data)

def generate_html(candidates_by_party_region):
    all_parties = list(sorted({party for party, _region in candidates_by_party_region.keys()}))
    all_regions = list(sorted({region for _party, region in candidates_by_party_region.keys()}))
    setting_list = ['gender', 'email', 'twitter', 'facebook', 'image', 'contact']

    yield '<link href="eu-candidate-grid.css" rel="stylesheet" type="text/css" />'
    yield '<div class="candidate-grid">'

    for setting in setting_list:
        yield '<span tabindex="1" class="candidate-grid-setting" id="{setting}">'.format(setting=setting)

    yield '<div class="headings">'
    for setting in setting_list:
        yield '<a class="heading heading-{setting}" href="#{setting}" onclick="document.getElementById(&quot;{setting}&quot;).focus(); return false;">{setting}</a>'.format(setting=setting)
    yield '</div>'

    yield '<table>'
    for party in all_parties:
        yield '<tr class="party-{party}">'.format(party=party)
        yield '<th>{party}</th>'.format(party=party)
        for region in all_regions:
            key = (party, region)
            yield '<td>'
            for candidate in candidates_by_party_region[key]:
                class_list = [
                    'candidate',
                    'pos-{}'.format(candidate['party_list_position']),
                    'gender-{}'.format(candidate['gender']),
                    'twitter-{}'.format('yes' if candidate['twitter_user_id'] else 'no'),
                    'facebook-{}'.format('yes' if candidate['facebook_page_url'] or candidate['facebook_personal_url'] else 'no'),
                    'image-{}'.format('yes' if candidate['image_url'] else 'no'),
                    'email-{}'.format('yes' if candidate['email'] else 'no'),
                    ]
                yield '<a href="https://whocanivotefor.co.uk/person/{cand_id}/" title="{name}" class="{csvclass}"></a>'.format(
                    cand_id=candidate['id'],
                    name=candidate['name'],
                    csvclass=' '.join(class_list))
            yield '</td>'
        yield '</tr>'
    yield '</table>'
    for _setting in setting_list:
        yield '</span>'
    yield '</div>'
    

def main():
    candidates_by_party_region = get_data()
    html = ''.join(generate_html(candidates_by_party_region))
    with open('eu-candidate-grid.html', 'w') as f:
        f.write(html)

if __name__ == '__main__':
    main()
