from flask import Flask,render_template,url_for
app=Flask(__name__)
def getPosts():
    posts=[{'name': " An introduction to numpy"
            , 'author':" jane doe", 'date_posted':'28/02/20','content':" matrix manipulation is done in numpy",
            'difficulty_level':4},
           {'name': " An introduction to pandas"
               , 'author': " joe doe", 'date_posted': '18/02/20',
            'difficulty_level': 1,'content':' pandas is for data frames'}
    ]
    return posts
@app.route("/")
def hello():
    return render_template('Homepage.html',title="Blog app!!!!",posts=getPosts())
@app.route("/contactus")
def contactus():
    return render_template('Contactus.html')
if __name__=="__main__":
    app.run(debug=True)


