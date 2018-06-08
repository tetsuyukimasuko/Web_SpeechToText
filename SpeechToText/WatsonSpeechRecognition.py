from watson_developer_cloud import SpeechToTextV1
import re

class WatsonSTT():

    #初期化処理で認証情報を入れる
    def __init__(self,uname,pword):
        self.user_name=uname
        self.url='https://stream.watsonplatform.net/speech-to-text/api'
        self.password=pword
        self.speech_to_text=SpeechToTextV1(username=self.user_name,password=self.password,url=self.url)


    #カスタムモデルの作成を行う関数。
    def CreateCustomModel(self,model_name,model='ja'):
        
        #多言語対応
        if model=='ja':
            base_model='ja-JP_BroadbandModel'
        elif model=='en':
            base_model='en-US_BroadbandModel'       
        
        custom_model=self.speech_to_text.create_language_model(model_name,base_model)
        return custom_model['customization_id']

    #カスタムモデルの削除
    def DeleteCustomModel(self,id):
        self.speech_to_text.delete_language_model(id)

    #カスタムモデルの単語を更新する関数
    #辞書を渡す。例 : {'部長' : ['ブチョウ','ブチョー'], '課長' : ['カチョウ','カチョー']}
    #既にある単語が指定された場合は、読み仮名が同じかどうかを調査し、違う場合は更新する。同じ場合は無視する。
    #渡した辞書にない単語は削除される。
    #TODO lockedのエラーが出たときにちゃんとエラーを出力する
    def AddCustomWords(self,model_id,dict):
        keys=list(dict.keys())
        word_list=self.speech_to_text.list_words(model_id)
        word_list=word_list['words']
        existing_word=[]
        existing_sound=[]
        new_word_input=False

        if len(word_list)>0:
            for i in range(len(word_list)):
                word_name=word_list[i]['word']
                word_sound=word_list[i]['sounds_like']
                existing_word.append(word_name)
                existing_sound.append(word_sound)

        for i in range(len(keys)):
            if keys[i] in existing_word:
                j=existing_word.index(keys[i])
                if set(dict[keys[i]])==set(existing_sound[j]):
                    print('単語',keys[i],'は登録済みです。')
                else:
                    print('単語',keys[i],'は登録済みですが、読み仮名を更新します。')
                    self.speech_to_text.delete_word(model_id,keys[i])
                    sound=dict[keys[i]]
                    self.speech_to_text.add_word(model_id,keys[i],sound)
                    new_word_input=True
                existing_word.remove(keys[i])
                existing_sound.remove(existing_sound[j])
            else:
                sound=dict[keys[i]]
                print('単語',keys[i],'を新規登録します。')
                self.speech_to_text.add_word(model_id,keys[i],sound)
                new_word_input=True

        #渡さなかった単語の削除
        deleted_word=[]
        for tmp in existing_word:
            print('単語',tmp,'を削除します。')
            new_word_input=True
            deleted_word.append(tmp)

        if len(deleted_word)>0:    
            self.DeleteCustomWords(model_id,deleted_word)

        #トレーニング
        if new_word_input:
            tr=self.speech_to_text.train_language_model(model_id)

        #登録済み単語リスト出力
        word_list=self.speech_to_text.list_words(model_id)
        word_list=word_list['words']
        results={}
        if len(word_list)>0:
            for i in range(len(word_list)):
                word_name=word_list[i]['word']
                word_sound=word_list[i]['sounds_like']
                results.setdefault(word_name,word_sound)
        return results

    #登録されている単語をゲットする関数
    def GetCustomWords(self,model_id):
        #登録済み単語リスト出力
        word_list=self.speech_to_text.list_words(model_id)
        word_list=word_list['words']
        results={}
        if len(word_list)>0:
            for i in range(len(word_list)):
                word_name=word_list[i]['word']
                word_sound=word_list[i]['sounds_like']
                results.setdefault(word_name,word_sound)
        return results


    #カスタムモデルのidを全部持ってくる
    def ListCustomModels(self):
        results=[]
        custom_models=self.speech_to_text.list_language_models()
        models=custom_models['customizations']
        if len(models)>0:
            for i in range(len(models)):
                results.append(models[i]['customization_id'])
        return results


    #指定した名前のカスタムモデルのidを持ってくる
    def GetCustomModelByName(self,name):
        result=''
        custom_models=self.speech_to_text.list_language_models()
        models=custom_models['customizations']
        if len(models)>0:
            for i in range(len(models)):
                tmp=models[i]['name']
                if tmp==name:
                    result=models[i]['customization_id']
        return result



    #単語を削除する。wordsはlist
    def DeleteCustomWords(self,model_id,words):
        word_list=self.speech_to_text.list_words(model_id)
        word_list=word_list['words']

        existing_word=[]

        if len(word_list)>0:
            for i in range(len(word_list)):
                word_name=word_list[i]['word']
                existing_word.append(word_name)

        for word in words:
            if word in existing_word:
                #print(word,'を削除します。')
                self.speech_to_text.delete_word(model_id,word)
            else:
                #print(word,'なんて単語はありませんよ。')
                pass

    #音声認識を行う。セッションレス。
    def RecognizeAudio(self,file,delete_interjection=True,customization_id=None,customization_weight=0.3,model='ja'):

        #多言語対応
        if model=='ja':
            base_model='ja-JP_BroadbandModel'
        elif model=='en':
            base_model='en-US_BroadbandModel'

        #with open(file,'rb') as audio_file:
        audio_file=file
        try:
            if customization_id==None:
                r=self.speech_to_text.recognize(
                            audio=audio_file,
                            content_type='audio/wav',
                            timestamps=True,
                            word_confidence=True,
                            model=base_model
                            )
            else:
                r=self.speech_to_text.recognize(
                            audio=audio_file,
                            content_type='audio/wav',
                            timestamps=True,
                            word_confidence=True,
                            model=base_model,
                            customization_id=customization_id,
                            customization_weight=customization_weight
                            )

            tmp=r['results']

        except:
            tmp=[]

        transcripts=''

        if len(tmp)>0:
            for i in range(len(tmp)):
                #timestampに分ける
                results=r['results'][i]['alternatives'][0]['timestamps']
                tmp_result=''
                for result in results:
                    tmp_text=result[0]

                    #あいづちを除く
                    if delete_interjection:
                        mo=re.findall(r'D_\w+',tmp_text)
                        if len(mo)>0:
                            pass
                        else:
                            tmp_result+=tmp_text
                    else:
                        tmp_result+=tmp_text

                transcripts+=tmp_result.replace(' ','')

                #句読点を足す
                if model=='ja':
                    transcripts+='。\n'
                elif model=='en':
                    transcripts+='.\n'


        if transcripts=='':
            transcripts='unrecognized'

        #transcript=self.kansuji2arabic(transcript,sep=True)

        return transcripts

    #漢数字をアラビア数字に変換
    #https://qiita.com/dosec/items/c6aef40fae6977fd89ab
    def kansuji2arabic(self,kstring, sep=False):
        
        tt_ksuji = str.maketrans('一二三四五六七八九〇壱弐参', '1234567890123')

        re_suji = re.compile(r'[十拾百千万億兆\d]+')
        re_kunit = re.compile(r'[十拾百千]|\d+')
        re_manshin = re.compile(r'[万億兆]|[^万億兆]+')

        TRANSUNIT = {'十': 10,
                     '拾': 10,
                     '百': 100,
                     '千': 1000}
        TRANSMANS = {'万': 10000,
                     '億': 100000000,
                     '兆': 1000000000000}

        def _transvalue(sj, re_obj=re_kunit, transdic=TRANSUNIT):
            unit = 1
            result = 0
            for piece in reversed(re_obj.findall(sj)):
                if piece in transdic:
                    if unit > 1:
                        result += unit
                    unit = transdic[piece]
                else:
                    val = int(piece) if piece.isdecimal() else _transvalue(piece)
                    result += val * unit
                    unit = 1

            if unit > 1:
                result += unit

            return result

        transuji = kstring.translate(tt_ksuji)
        for suji in sorted(set(re_suji.findall(transuji)), key=lambda s: len(s),
                               reverse=True):
            if not suji.isdecimal():
                arabic = _transvalue(suji, re_manshin, TRANSMANS)
                arabic = '{:,}'.format(arabic) if sep else str(arabic)
                transuji = transuji.replace(suji, arabic)

        return transuji

    #セッションを使う。非同期通信に需要はないかもしれないが一応。
    def RecognizeAudioWithSession(self,audio_file,delete_interjection=True,customization_id=None,customization_weight=0.3,model='ja'):
        
         #多言語対応
        if model=='ja':
            base_model='ja-JP_BroadbandModel'
        elif model=='en':
            base_model='en-US_BroadbandModel'       
        
        #ここは送信形式でかえる
        try:
            if customization_id==None:
                r=self.speech_to_text.create_job(audio_file,'audio/wav',model=base_model,timestamps=True)
            else:
                model_info=self.speech_to_text.get_language_model(customization_id)
                base_model=model_info['base_model_name']
                r=self.speech_to_text.create_job(audio_file,'audio/wav',model='ja-JP_BroadbandModel',timestamps=True,customization_id=customization_id, customization_weight=customization_weight)

            job_id=r['id']
        except:
            pass

        while True:
            result=self.speech_to_text.check_job(job_id)
            stat=result['status']
            if stat=='completed':
                self.speech_to_text.delete_job(job_id)
                break

        count=len(result['results'])
        transcripts=''

        for i in range(count):

            results_len=len(result['results'][i]['results'])
            
            for j in range(results_len):
                
                #この中にalternativeがある。
                alternatives=result['results'][i]['results'][j]['alternatives']

                #今回は、最もconfidenceが高い、0番目のみを持ってくる。
                timestamps=alternatives[0]['timestamps']

                tmp_result=''

                for t in timestamps:
                    if delete_interjection:
                        mo=re.findall(r'D_\w+',t[0])
                        if len(mo)==0:
                            tmp_result+=t[0]
                    else:
                        tmp_result+=t[0]

                tmp_result=tmp_result.replace(' ','')
                transcripts+=tmp_result

                #まだ回りきっていなければ、発言と発言の間に空白を入れる
                if j<results_len-1:
                    transcripts+='。\n'      
        
        if transcripts=='':
            transcripts='unrecognized'

        transcripts=self.kansuji2arabic(transcripts,sep=True)

        return transcripts


