import requests 
import time
import csv
from datetime import datetime, date
  
# api-endpoint 
url_review = "https://api.wanikani.com/v2/reviews"
url_subjects = "https://api.wanikani.com/v2/subjects"

# File paths
path_reviews = 'reviews.csv'
path_subjects = 'subjects.csv'
path_daystats = 'daystats.csv'
  
# Param values
update_after = "1970-01-01T00:00:00.000Z"
api_V2 = ""
  
# defining a params dict for the parameters to be sent to the API 
PARAMS = {'update_after': update_after} 
HEADERS = {'Wanikani-Revision': '20170710', 'Authorization': f"Bearer {api_V2}"}

SUBJECTS = open(path_subjects, "a", encoding="utf-8")
DAYSTATFILE = open(path_daystats, "w", encoding="utf-8")
DAYSTATSHEADERS = [
      'Date',
      'Item Reviews Done',
      'Apprentice',
      'Guru',
      'Master',
      'Enlightened',
      'Burned',
      'Total Active',
      'Total Items',
      'Kanji Reading Acc',
      'Kanji Meaning Acc',
      'Vocab Reading Acc',
      'Vocab Meaning Acc',
      'Radical Acc',
      'Kanji Acc',
      'Vocab Acc',
      'Reading Acc',
      'Meaning Acc',
      'Total Acc',
      'Total Reading Reviews',
      'Total Incorrect Readings',
      'Total Meaning Reviews',
      'Total Incorrect Meaning',
      'Total Review Number',
      'Total Incorrect Answer',
      'Total Correct Answers',
      'Kanji Guru+',
      'Vocab Guru+',
      'Level'
]
DAYSTATFILE.write(f'{";".join(DAYSTATSHEADERS)}\n')

OBJECTS = {}
DAYSTATS = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0}


def is_empty(file_name):
      with open(file_name, 'r', encoding="utf-8") as read_obj:
        # read first character
        one_char = read_obj.read(1)
        # if not fetched then file is empty
        if not one_char:
           return True
      return False

def cache_subjects():
      with open(path_subjects,'w', newline='', encoding="utf-8") as csvfile:
            fieldnames = ['subject_id', 'subject_level','subject_type','characters']
            writer = csv.DictWriter(csvfile, delimiter=';', fieldnames=fieldnames)
            writer.writeheader()
      while True:
            r = requests.get(url = url_subjects, params = PARAMS, headers = HEADERS)
            data = r.json()
            for entry in data['data']:
                  subject_id = entry['id']
                  subject_type = entry['object']
                  subject_level = entry['data']['level']
                  characters = entry['data']['characters']
                  OBJECTS[subject_id] = {
                        'level' : subject_level,
                        'subject_type' : subject_type,
                        'characters' : characters
                  }
                  SUBJECTS.write(f'{subject_id};{subject_level};{subject_type};{characters}\n')
            URL_SUBJECTS = data['pages']['next_url']
            print(f'Current subject request completed, requesting {URL_SUBJECTS}')
            if (URL_SUBJECTS is None):
                  break

def load_subjects():
      with open(path_subjects,'r', newline='', encoding="utf-8") as csvfile:
            csvreader = csv.DictReader(csvfile, delimiter=';', quotechar='|')
            for row in csvreader:
                  OBJECTS[row['subject_id']] = {
                        'level' :row['subject_level'],
                        'subject_type' :row['subject_type'],
                        'characters' :row['characters']
                        }

## If subjects are not cached, they will be downloaded from the API
def get_subjects():
      if is_empty(path_subjects):
            print(f"Subjects not cached. Initializing file.")
            cache_subjects()
      else:
            print(f"Subjects cached. Reading file.")
            load_subjects()

def get_accuracy(correct, incorrect):
      return 0 if correct == 0 else ((correct) / (correct + incorrect)) * 100

def get_cumulative_acc(cum,total):
      return 0 if total == 0 else cum / total

# Open the reviews file for writing
def get_reviews(review_path, api_url):

      # Specific the data to be saved
      CurrentDay = None
      checked = 0
      daily_reviews = 0
      total_reviews = 0
      total_answers = 0
      total_accuracy = 0
      total_reviews = 0
      total_correct = 0
      level = 1

      reading_accuracy = 0
      total_reading = 0
      total_reading_incorrect = 0
      total_reading_correct = 0

      meaning_accuracy = 0
      total_meaning = 0
      total_meaning_incorrect = 0
      total_meaning_correct = 0
      
      radical_meaning_correct = radical_meaning_incorrect = 0
      radical_accuracy = 0

      kanji_meaning_correct = kanji_meaning_incorrect = kanji_reading_correct = kanji_reading_incorrect = 0 
      kanji_accuracy = 0
      kanji_guruplus = 0

      vocab_meaning_correct = vocab_meaning_incorrect = vocab_reading_correct = vocab_reading_incorrect = 0
      vocab_accuracy = 100
      vocab_guruplus = 0
      

      f = open(review_path, "w")
      # Write the header
      f.write(f'subject_id;subject_type;created_at;starting_srs_stage;starting_srs_stage_name;ending_srs_stage;ending_srs_stage_name;incorrect_meaning_answers;incorrect_reading_answers\n')
      
      URL = api_url

      def write_dayrow():
            total_active = DAYSTATS[1] + DAYSTATS[2] + DAYSTATS[3] + DAYSTATS[4]+ DAYSTATS[5] + DAYSTATS[6] +DAYSTATS[7] + DAYSTATS[8]

            kanji_reading_acc = 0 if not kanji_reading_correct and not kanji_reading_incorrect else kanji_reading_correct / (kanji_reading_correct + kanji_reading_incorrect)
            kanji_meaning_acc = 0 if not kanji_meaning_correct and not kanji_meaning_incorrect else kanji_meaning_correct / (kanji_meaning_correct + kanji_meaning_incorrect)
            vocab_reading_acc = 0 if not vocab_reading_correct and not vocab_reading_incorrect else vocab_reading_correct / (vocab_reading_correct + vocab_reading_incorrect)
            vocab_meaning_acc = 0 if not vocab_meaning_correct and not vocab_meaning_incorrect else vocab_meaning_correct / (vocab_meaning_correct + vocab_meaning_incorrect)

            daystatsrows = {
                  'date': str(CurrentDay),
                  'item_reviews': daily_reviews,
                  'apprentice': DAYSTATS[1] + DAYSTATS[2] + DAYSTATS[3] + DAYSTATS[4],
                  'guru':DAYSTATS[5] + DAYSTATS[6],
                  'master':DAYSTATS[7],
                  'enlightened':DAYSTATS[8],
                  'burned':DAYSTATS[9],
                  'total_active': total_active,
                  'total_items': total_active + DAYSTATS[9],
                  'kanji_reading_acc':str(round(kanji_reading_acc,2)),
                  'kanji_meaning_acc':str(round(kanji_meaning_acc,2)),
                  'vocab_reading_acc':str(round(vocab_reading_acc,2)),
                  'vocab_meaning_acc':str(round(vocab_meaning_acc,2)),
                  'radical_acc':str(round(radical_accuracy,2)),
                  'kanji_acc':str(round(kanji_accuracy,2)),
                  'vocab_acc':str(round(vocab_accuracy,2)),
                  'reading_acc':str(round(reading_accuracy,2)),
                  'meaning_acc':str(round(meaning_accuracy,2)),
                  'total_acc':str(round(total_accuracy,2)),
                  'total_reading_Reviews': total_reading,
                  'total_incorrect_Readings': total_reading_incorrect,
                  'total_meaning_Reviews': total_meaning,
                  'total_incorrect_Meaning':total_meaning_incorrect,
                  'total_review_Number': total_reviews,
                  'total_incorrect_Answer': (total_reading_incorrect + total_meaning_incorrect),
                  'total_correct_Answers': total_correct,
                  'Kanji_guru_plus': kanji_guruplus,
                  'Vocab_guru_plus': vocab_guruplus,
                  'Level':level
            }
            # Make sure the rows and headers are the same length 
            # This is a debug check or if you add your own rows & Headers
            if (len(DAYSTATSHEADERS) != len(daystatsrows)):
                  raise Exception(f'Length of Daystats headers and daystats rows does not match: {len(daystatsrows)} & {len(DAYSTATSHEADERS)}')
            daystring = ';'.join(str(x) for x in daystatsrows.values())
            DAYSTATFILE.write(f'{daystring}\n')
      
      while True:
            r = requests.get(url = URL, params = PARAMS, headers = HEADERS)
            data = r.json()
            total_count = int(data['total_count'])
            for entry in data['data']:

                  # Get data from the Wanikani api request
                  starting_srs_stage = entry['data']['starting_srs_stage']
                  starting_srs_stage_name = entry['data']['starting_srs_stage_name']
                  ending_srs_stage = entry['data']['ending_srs_stage']
                  ending_srs_stage_name = entry['data']['ending_srs_stage_name']
                  subject_id = str(entry['data']['subject_id'])
                  incorrect_meaning_answers = entry['data']['incorrect_meaning_answers']
                  incorrect_reading_answers = entry['data']['incorrect_reading_answers']
                  subject_type = ""
                  created_at = str(entry['data']['created_at'][0:10])
                  date = datetime.strptime(created_at, "%Y-%m-%d").date()

                  # Retrieve the subject type from the cached subjects
                  subject_type = OBJECTS[subject_id]['subject_type']
                  subject_level =  int(OBJECTS[subject_id]['level'])

                  # The first day is not initialized so this is set on the first run
                  if (not CurrentDay): CurrentDay = date

                  # Check if the date has changed
                  # If yes, write a row in the file
                  if date > CurrentDay:
                        write_dayrow()
                        CurrentDay = date
                        # Reset daily review values
                        daily_reviews = 0

                  meaning_correct = 1 if incorrect_meaning_answers == 0 else 0
                  reading_correct = 0 if subject_type == 'radical' else (1 if incorrect_reading_answers == 0 else 0)
                  
                  # Calculate radical accuracies and update total and daily review counts
                  if (subject_type == 'radical'):
                        radical_meaning_correct += meaning_correct
                        radical_meaning_incorrect += incorrect_meaning_answers
                  # Calculate kanji accuracies and update total and daily review counts
                  elif (subject_type == 'kanji'):
                        kanji_meaning_correct += meaning_correct
                        kanji_meaning_incorrect += incorrect_meaning_answers
                        kanji_reading_correct += reading_correct
                        kanji_reading_incorrect += incorrect_meaning_answers
                         # Increase guruplus if level up to 5 happens
                        if (ending_srs_stage == 5 and starting_srs_stage == 4):
                              kanji_guruplus += 1
                        elif (ending_srs_stage < 5 and starting_srs_stage >= 5):
                              kanji_guruplus -= 1
                  # Calculate vocabulary accuracies and update total and daily review counts
                  elif (subject_type == 'vocabulary'):
                        vocab_meaning_correct += meaning_correct
                        vocab_meaning_incorrect += incorrect_meaning_answers
                        vocab_reading_correct += reading_correct
                        vocab_reading_incorrect += incorrect_meaning_answers
                        # Increase guruplus if level up to 5 happens
                        if (ending_srs_stage == 5 and starting_srs_stage == 4):
                              vocab_guruplus += 1
                        elif (ending_srs_stage < 5 and starting_srs_stage >= 5):
                              vocab_guruplus -= 1

                  # Update the amount of items in specific level 
                  DAYSTATS[starting_srs_stage] = DAYSTATS[starting_srs_stage] - 1 if DAYSTATS[starting_srs_stage] >= 1 else 0
                  DAYSTATS[ending_srs_stage] += 1

                  total_meaning_incorrect += incorrect_meaning_answers
                  total_reading_incorrect += incorrect_reading_answers
                  total_meaning_correct += meaning_correct
                  total_reading_correct += reading_correct

                  total_radical_reviews = radical_meaning_correct + radical_meaning_incorrect
                  total_kanji_reviews = kanji_meaning_correct + kanji_meaning_incorrect + kanji_reading_correct + kanji_reading_incorrect
                  total_vocab_reviews = vocab_meaning_correct + vocab_meaning_incorrect + vocab_reading_correct + vocab_reading_incorrect

                  total_correct = total_meaning_correct + total_reading_correct
                  total_incorrect  = total_meaning_incorrect + total_meaning_incorrect

                  total_meaning = (total_meaning_correct + total_meaning_incorrect)
                  total_reading = (total_reading_correct + total_reading_incorrect)
                  total_reviews = total_meaning + total_reading

                  total_accuracy = total_correct / total_reviews
                  radical_accuracy = radical_meaning_correct / total_radical_reviews
                  kanji_accuracy = 0 if not total_kanji_reviews else (kanji_reading_correct + kanji_meaning_correct) / total_kanji_reviews
                  vocab_accuracy = 0 if not total_vocab_reviews else (vocab_reading_correct + vocab_meaning_correct) / total_vocab_reviews
                  meaning_acc = 0 if not total_meaning_correct and not total_meaning_incorrect else total_meaning_correct / (total_meaning_correct + total_meaning_incorrect)
                  reading_acc = 0 if not total_reading_correct and not total_reading_incorrect else total_reading_correct / (total_reading_correct + total_reading_incorrect)

                  total_answers += (total_reading + total_meaning)
                  total_reviews += (total_correct + total_incorrect)
                  daily_reviews +=1
            
                  # Checks if the next level is, well, the next one
                  # This is because for some reason I had a level 29 radical at level 7 reviews
                  if (subject_level == (level + 1)):
                        level = subject_level
                        char = OBJECTS[subject_id]['characters']
                  # If you want to have reviews in an csv format, uncomment the following line.
                  #f.write(f'{subject_id};{subject_type};{created_at};{starting_srs_stage};{starting_srs_stage_name};{ending_srs_stage};{ending_srs_stage_name};{incorrect_meaning_answers};{incorrect_reading_answers}\n')
                  checked += 1
            URL = data['pages']['next_url']
            print(f'{str(round((checked / total_count),2)*100)}% completed. Requesting {URL}')
            if (URL is None): 
                  # Write the last row
                  write_dayrow()
                  break

if __name__ == "__main__":
      start = time.time()
      get_subjects()
      get_reviews(path_reviews, url_review)
      end = time.time()
      print(f'Done!')
      print(f'Time elapsed: {str(round(end - start,2))}s')
