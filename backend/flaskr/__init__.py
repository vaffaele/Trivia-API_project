import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app)

  def pagination(request,total):

      page=request.args.get('page',1,type=int)
      start = (page-1)*QUESTIONS_PER_PAGE
      end = start+QUESTIONS_PER_PAGE
      questions=[question.format() for question in total]
      questions_per_page = questions[start:end]
      return questions_per_page


  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers','Content-type, Authorization')
      response.headers.add('Access-Control-Allow-Methods','GET,POST,PUT,PATCH,DELETE,OPTIONS')
      return response


  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''

  '''
  @TODO:
  Create an endpoint to handle GET requests
  for all available categories.
  '''
  @app.route('/categories')
  def get_categories():
      categories = Category.query.all()
      dict={}
      for category in categories:
          dict[category.id]=category.type
      if(len(dict)==0):
          abort(404)

      return jsonify({
      'success':True,
      'categories':dict
      })


  '''
  @TODO:
  Create an endpoint to handle GET requests for questions,
  including pagination (every 10 questions).
  This endpoint should return a list of questions,
  number of total questions, current category, categories.



  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions.
  '''
  @app.route('/questions')
  def get_questons_for_category():

       questions = Question.query.all()
       categories = Category.query.all()
       questions_per_page=pagination(request,questions)

       dict={}
       for category in categories:
           dict[category.id]=category.type

       if (len(questions_per_page)==0):
           abort(404)

       return jsonify({
       'success':True,
       'questions':questions_per_page,
       'total_questions': len(questions),
       'categories': dict
       })

  '''
  @TODO:
  Create an endpoint to DELETE question using a question ID.


  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page.
  '''
  @app.route('/questions/<int:question_id>',methods=['DELETE'])
  def delete_question(question_id):
        try:
          delete_question = Question.query.get(question_id)
          Question.delete(delete_question)
          if delete_question==None:

              abort(404)


          return jsonify({
           'success':True,
           'deleted':question_id
          })
        except:
          abort(422)

  '''
  @TODO:
  Create an endpoint to POST a new question,
  which will require the question and answer text,
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab,
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.
  '''
  @app.route('/questions',methods=['POST'])
  def create_question():

       body= request.get_json()


       if len(body)==1:
           search=body['searchTerm']
           questions_search = Question.query.filter(Question.question.ilike('%'+search+'%')).all()
           if len(questions_search)==0:
                abort(404)
           questions_per_page=pagination(request,questions_search)
           return jsonify({
           'success':True,
           'questions':questions_per_page,
           'total_questions':len(questions_search)
           })
       else:

            try:
               question=body['question']
               answer=body['answer']
               category=body['category']
               difficulty=body['difficulty']

               if len(question)==0 or len(answer)==0 :

                   abort(400)
               new_question = Question(question=question, answer=answer, category=category,difficulty=difficulty)
               Question.insert(new_question)
               id_new=new_question.id
               questions = Question.query.all()
               categories = Category.query.all()
               questions_per_page=pagination(request,questions)

               dict={}
               for category in categories:
                   dict[category.id]=category.type
               return jsonify({
               'success':True,
               'created':id_new
              
               })
            except:
              abort(422)

  '''
  @TODO:
  Create a POST endpoint to get questions based on a search term.
  It should return any questions for whom the search term
  is a substring of the question.

  TEST: Search by any phrase. The questions list will update to include
  only question that include that string within their question.
  Try using the word "title" to start.
  '''



  '''
  @TODO:
  Create a GET endpoint to get questions based on category.

  TEST: In the "List" tab / main screen, clicking on one of the
  categories in the left column will cause only questions of that
  category to be shown.
  '''
  @app.route('/categories/<int:category_id>/questions')
  def get_questions_for_category(category_id):
      questions = Question.query.filter_by(category=str(category_id)).all()
      questions_per_page=pagination(request,questions)
      category = Category.query.filter_by(id=category_id).one_or_none()
      dict={}
      dict[category.id]=category.type

      return jsonify({
      'success':True,
      'questions':questions_per_page,
      'total_questions': len(questions),
      'categories': dict

      })


  '''
  @TODO:
  Create a POST endpoint to get questions to play the quiz.
  This endpoint should take category and previous question parameters
  and return a random questions within the given category,
  if provided, and that is not one of the previous questions.

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not.
  '''
  @app.route('/quizzes',methods=['POST'])
  def get_quiz():
        print(request)
        json_body=request.get_json()
        print(json_body)
        quiz_category=json_body['quiz_category']
        previous_questions=json_body['previous_questions']
        id=quiz_category['id']
        type=quiz_category['type']


        try:
           id=quiz_category['id']
           type=quiz_category['type']
           if len(id)==0 or len(type)==0:
                    print(id,type)
                    abort(422)

           elif id==0:

               questions = Question.query.all()
               i=random.randint(1,len(questions))
               question=questions[i-1]
               return jsonify({
               'success':True,
               'question':question.format()
               })
           else:

               questions = Question.query.filter_by(category=id).all()

               for i in range(len(questions)):
                   if len(questions)==len(previous_questions):
                       return jsonify({
                       'success':True,
                       })
                       break
                   else:
                       i=random.randint(1,len(questions))
                       question=questions[i-1]
                       if not is_used(previous_questions,question):
                           break

               return jsonify({
               'success':True,
               'question':question.format()
               })
        except:
            abort(422)
  '''
  @TODO:
  Create error handlers for all expected errors
  including 404 and 422.
  '''

  @app.errorhandler(400)
  def bad_request(error):
      return jsonify({
        'success':False,
        'error': 400,
        'message':'bad request'
      }),400

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success':False,
      'error': 404,
      'message':'not found'
    }),404

  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify({
        'success':False,
        'error': 422,
        'message':'unprocessable'
      }),422



  def is_used(previous_questions,current_question):
      is_used=False

      if len(previous_questions)==0:
              is_used=False
      elif current_question.id in previous_questions:
              is_used=True

      return is_used



  return app
