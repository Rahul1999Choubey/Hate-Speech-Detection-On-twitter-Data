#!/usr/bin/env python
# coding: utf-8

# In[1]:


# import the required libraries
import pandas as pd
import numpy as np
import re
import seaborn as sns


# In[2]:


import matplotlib.pyplot as plt
from matplotlib import style
style.use('ggplot')


# In[3]:


from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords



# In[4]:


stop_words = set(stopwords.words('english'))


# In[5]:


from wordcloud import WordCloud
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, ConfusionMatrixDisplay


# In[6]:


tweet_df = pd.read_csv(r'C:\Users\Rahul Choubey\Downloads\train\train.csv')


# In[7]:


tweet_df.head()


# In[8]:


tweet_df.info()


# In[35]:


# printing random tweets 
print(tweet_df['tweet'].iloc[0],"\n")
print(tweet_df['tweet'].iloc[1],"\n")
print(tweet_df['tweet'].iloc[2],"\n")
print(tweet_df['tweet'].iloc[3],"\n")
print(tweet_df['tweet'].iloc[4],"\n")


# In[12]:


#creating a function to process the data
def data_processing(tweet):
    tweet = tweet.lower()
    tweet = re.sub(r"https\S+|www\S+http\S+", '', tweet, flags = re.MULTILINE)
    tweet = re.sub(r'\@w+|\#','', tweet)
    tweet = re.sub(r'[^\w\s]','',tweet)
    tweet = re.sub(r'ð','',tweet)
    tweet_tokens = word_tokenize(tweet)
    filtered_tweets = [w for w in tweet_tokens if not w in stop_words]
    return " ".join(filtered_tweets)


# In[22]:


tweet_df.tweet = tweet_df['tweet'].apply(data_processing)


# In[23]:


tweet_df = tweet_df.drop_duplicates('tweet')


# In[26]:


lemmatizer = WordNetLemmatizer()
def lemmatizing(data):
    tweet = [lemmatizer.lemmatize(word) for word in data]
    return data


# In[33]:


tweet_df['tweet'] = tweet_df['tweet'].apply(lambda x: lemmatizing(x))


# In[34]:


# printing the data to see the effect of preprocessing
print(tweet_df['tweet'].iloc[0],"\n")
print(tweet_df['tweet'].iloc[1],"\n")
print(tweet_df['tweet'].iloc[2],"\n")
print(tweet_df['tweet'].iloc[3],"\n")
print(tweet_df['tweet'].iloc[4],"\n")


# In[35]:


tweet_df.info()


# In[36]:


tweet_df['label'].value_counts()


# ### Data visualization 

# In[37]:


fig = plt.figure(figsize=(5,5))
sns.countplot(x='label', data = tweet_df)


# In[38]:


fig = plt.figure(figsize=(7,7))
colors = ("red", "gold")
wp = {'linewidth':2, 'edgecolor':"black"}
tags = tweet_df['label'].value_counts()
explode = (0.1, 0.1)
tags.plot(kind='pie',autopct = '%1.1f%%', shadow=True, colors = colors, startangle =90, 
         wedgeprops = wp, explode = explode, label='')
plt.title('Distribution of sentiments')


# In[39]:


non_hate_tweets = tweet_df[tweet_df.label == 0]
non_hate_tweets.head()


# In[40]:


text = ' '.join([word for word in non_hate_tweets['tweet']])
plt.figure(figsize=(20,15), facecolor='None')
wordcloud = WordCloud(max_words=500, width=1600, height=800).generate(text)
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title('Most frequent words in non hate tweets', fontsize = 19)
plt.show()


# In[41]:


neg_tweets = tweet_df[tweet_df.label == 1]
neg_tweets.head()


# In[42]:


text = ' '.join([word for word in neg_tweets['tweet']])
plt.figure(figsize=(20,15), facecolor='None')
wordcloud = WordCloud(max_words=500, width=1600, height=800).generate(text)
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title('Most frequent words in hate tweets', fontsize = 19)
plt.show()


# In[43]:


vect = TfidfVectorizer(ngram_range=(1,2)).fit(tweet_df['tweet'])


# In[44]:


feature_names = vect.get_feature_names()
print("Number of features: {}\n".format(len(feature_names)))
print("First 20 features: \n{}".format(feature_names[:20]))


# In[45]:


vect = TfidfVectorizer(ngram_range=(1,3)).fit(tweet_df['tweet'])


# In[46]:


feature_names = vect.get_feature_names()
print("Number of features: {}\n".format(len(feature_names)))
print("First 20 features: \n{}".format(feature_names[:20]))


# ## Model Building

# In[47]:


X = tweet_df['tweet']
Y = tweet_df['label']
X = vect.transform(X)


# In[48]:


x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=42)


# In[49]:


print("Size of x_train:", (x_train.shape))
print("Size of y_train:", (y_train.shape))
print("Size of x_test: ", (x_test.shape))
print("Size of y_test: ", (y_test.shape))


# In[50]:


logreg = LogisticRegression()
logreg.fit(x_train, y_train)
logreg_predict = logreg.predict(x_test)
logreg_acc = accuracy_score(logreg_predict, y_test)
print("Test accuarcy: {:.2f}%".format(logreg_acc*100))


# In[51]:


print(confusion_matrix(y_test, logreg_predict))
print("\n")
print(classification_report(y_test, logreg_predict))


# In[52]:


style.use('classic')
cm = confusion_matrix(y_test, logreg_predict, labels=logreg.classes_)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=logreg.classes_)
disp.plot()


# In[53]:


from sklearn.model_selection import GridSearchCV
import warnings
warnings.filterwarnings('ignore')


# In[54]:


param_grid = {'C':[100, 10, 1.0, 0.1, 0.01], 'solver' :['newton-cg', 'lbfgs','liblinear']}
grid = GridSearchCV(LogisticRegression(), param_grid, cv = 5)
grid.fit(x_train, y_train)
print("Best Cross validation score: {:.2f}".format(grid.best_score_))
print("Best parameters: ", grid.best_params_)


# In[55]:


y_pred = grid.predict(x_test)


# In[56]:


logreg_acc = accuracy_score(y_pred, y_test)
print("Test accuracy: {:.2f}%".format(logreg_acc*100))


# In[57]:


print(confusion_matrix(y_test, y_pred))
print("\n")
print(classification_report(y_test, y_pred))


# In[ ]:




