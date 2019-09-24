'''
Xinru Yan
July 2019

This program reads input from DiscourseDB and prepare it for CSM

Usage:
    python gen_input_csm.py INPUT OUTPUT MODE
    python src/gen_input_csm.py -i src/analyzer/data_enviroaction.csv -o src/enviroaction.csv -m CSM
    Note that the MODE parameter can only take either 'Index' or 'CSM'
'''
import click
import csv
import nltk
import re
import string

exclude = set(string.punctuation)


def clean(text):
    # get rid of links
    text = re.sub(r'\(http\S+\)|http\S+|www.\S+|imgur.\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'•','',text,flags=re.MULTILINE)
    text = re.sub(r'\[|\]', '', text, flags=re.MULTILINE)
    # get rid of puncs
    text = ''.join(w for w in text if w not in exclude)
    text = re.sub(r'\s+', ' ', text, flags=re.MULTILINE)
    return text


@click.command()
@click.option('-i', '--input', 'input', type=str)
@click.option('-o', '--output', 'output', type=str)
@click.option('-m', '--mode', 'mode', type=str)
def main(input, output,mode):
    with open(output, 'w') as fo:
        csv_file = csv.writer(fo)
        if mode == 'Index':
            csv_file.writerow(['SeqId', 'InstNo', 'Author', 'Text', 'IndexRange'])
        else:
            csv_file.writerow(['SeqId', 'InstNo', 'Author', 'Text'])

        with open(input, 'r') as fi:
            csv_reader = csv.DictReader(fi)
            for row in csv_reader:
                original_content = row['content'].lower()
                content = row['content'].replace('\n', ' ').lower()
                content = nltk.tokenize.sent_tokenize(content)
                if len(content) > 4:
                    count = 0
                    index = 0
                    #print(original_content, len(original_content))
                    for sent in content:
                        sent = nltk.tokenize.word_tokenize(sent)
                        try:
                            sent_begin = sent[0] + ' ' + sent[1]
                        except IndexError:
                            continue
                        if len(sent) >= 4:
                            sent_end = ""
                            for a in range(-4, 0):
                                if sent[a] not in exclude and sent[a+1] not in exclude and a != -1:
                                    sent_end += sent[a] + ' '
                                else:
                                    sent_end += sent[a]
                        else:
                            try:
                                sent_end = sent[-2] + sent[-1]
                            except IndexError:
                                continue
                        if " '" in sent_begin:
                            sent_begin = sent_begin.replace(" '", "'")
                        if " '" in sent_end:
                            sent_end = sent_end.replace(" '", "'")
                        sent = ' '.join(sent)
                        if "’ " in sent:
                            sent = sent.replace("’ ", "’")

                        if original_content[index:].find(sent_begin) != -1:
                            index = original_content[index:].find(sent_begin) + index
                            index_end = original_content[index:].find(sent_end) + index - 1 + len(sent_end)
                            sent = clean(sent)
                            if mode == 'Index':
                                csv_file.writerow(
                                    [row['contributionId'], count, row['contributor'], sent, (index, index_end)])
                            else:
                                csv_file.writerow([row['contributionId'], count, row['contributor'], sent])
                            count += 1
                            index = index_end + 1


if __name__ == '__main__':
    main()
