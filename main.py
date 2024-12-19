from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import uuid
import logging
from logging.handlers import RotatingFileHandler
import traceback
import sys

# ロガーの設定
logger = logging.getLogger('flask_app')
logger.setLevel(logging.DEBUG)

# ファイルハンドラーの設定
file_handler = RotatingFileHandler(
    'app.log',
    maxBytes=1024 * 1024 * 1000,  # 1MB
    backupCount=10,
    encoding='utf-8'
)
file_handler.setLevel(logging.DEBUG)

# コンソールハンドラーの設定
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)

# フォーマッターの設定
formatter = logging.Formatter(
    '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# ハンドラーの追加
logger.addHandler(file_handler)
logger.addHandler(console_handler)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/database'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
db = SQLAlchemy(app)

# SQLAlchemyのログを有効化
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

class ReqMgr(db.Model):
    __tablename__ = 'req_mgr'
    id = db.Column(db.Integer, primary_key=True)
    req_uuid = db.Column(db.UUID, unique=True, nullable=False)

class Reqs(db.Model):
    __tablename__ = 'reqs'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    req_uuid = db.Column(db.UUID, nullable=False)
    mgr_id = db.Column(db.UUID, nullable=False)
    progress = db.Column(db.Integer)
    client_name = db.Column(db.VARCHAR(255))
    creator_name = db.Column(db.VARCHAR(255))
    tasks = db.Column(db.ARRAY(db.String))

    def __str__(self):
        return f"Req(id={self.id}, req_uuid={self.req_uuid}, progress={self.progress}, client_name={self.client_name}, creator_name={self.creator_name})"

def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        logger.error(f"Invalid UUID format: {val}")
        return False
    
@app.errorhandler(400)
def page_not_found(error):
    return render_template('40x.html'), 400

@app.errorhandler(404)
def page_not_found(error):
    return render_template('40x.html'), 404

@app.before_request
def log_request_info():
    logger.debug('Headers: %s', request.headers)
    logger.debug('Body: %s', request.get_data())

@app.route("/")
def index():
    logger.info('Accessing index page')
    return render_template("index.html")

@app.route("/delete")
def deleteitem():
    mgrid = request.args.get("id")
    reqid = request.args.get("req_id")
    
    logger.info(f"Attempting to delete item with mgr_id={mgrid}, req_id={reqid}")
    
    try:
        reqdata = Reqs.query.filter_by(mgr_id=mgrid, req_uuid=reqid).first()
        if reqdata:
            db.session.delete(reqdata)
            db.session.commit()
            logger.info(f"Successfully deleted item with mgr_id={mgrid}, req_id={reqid}")
        else:
            logger.warning(f"No item found with mgr_id={mgrid}, req_id={reqid}")
        return "OK", 200
    except Exception as e:
        logger.error(f"Error deleting item: {str(e)}\n{traceback.format_exc()}")
        return "Error", 500

@app.route("/req")
def req():
    logger.info("Accessing request page")
    if "req_id" in request.args:
        reqid = request.args.get("req_id")
        logger.debug(f"Request ID: {reqid}")
        
        try:
            reqdata = Reqs.query.with_entities(
                Reqs.progress, 
                Reqs.client_name,
                Reqs.creator_name,
                Reqs.tasks,
            ).filter_by(req_uuid=reqid).first()
            
            if reqdata:
                logger.debug(f"Found request data: {reqdata}")
            else:
                logger.warning(f"No request data found for req_id={reqid}")
            
            return render_template("req.html", reqdata=reqdata)
        except Exception as e:
            logger.error(f"Error retrieving request data: {str(e)}\n{traceback.format_exc()}")
            return "Error", 500
    
    return render_template("index.html", reqdata=[])

@app.route("/manage")
def manage():
    logger.info("Accessing manage page")
    if "id" not in request.args:
        logger.warning("No ID provided in manage request")
        return "管理番号が不正です。URLを確認してください。"
    
    mgr_id = request.args.get("id")
    if is_valid_uuid(mgr_id):
        try:
            reqs = Reqs.query.filter_by(mgr_id=mgr_id).all()
            logger.debug(f"Found {len(reqs)} requests for manager {mgr_id}")
            return render_template("manager.html", reqs=reqs)
        except Exception as e:
            logger.error(f"Error retrieving manager data: {str(e)}\n{traceback.format_exc()}")
            return "Error", 500
    else:
        return "Invalid manager ID", 400

@app.route("/reqedit", methods=["GET", "POST"])
def reqedit():
    logger.info(f"Accessing reqedit page - Method: {request.method}")
    
    if "id" not in request.args or "req_id" not in request.args:
        logger.warning("Missing required parameters in reqedit")
        return "編集権限がありません。", 200
    
    mgrid = request.args.get("id")
    reqid = request.args.get("req_id")
    logger.debug(f"Edit request for mgr_id={mgrid}, req_id={reqid}")
    
    try:
        if request.method == "POST":
            client_name = request.form.get("client_name")
            creator_name = request.form.get("creator_name")
            progress = request.form.get("progress")
            prog_text = request.form.getlist("progress_text")[::-1]
            
            logger.debug(f"POST data: client={client_name}, creator={creator_name}, progress={progress}")
            
            reqdata = Reqs.query.filter_by(mgr_id=mgrid, req_uuid=reqid).first()

            if reqdata:
                logger.info("Updating existing request")
                reqdata.creator_name = creator_name
                reqdata.client_name = client_name
                reqdata.progress = progress
                reqdata.tasks = prog_text
                db.session.commit()
            else:
                logger.warning("Request not found for update")
            
            return render_template("editor.html", reqdata=reqdata)
        
        reqdata = Reqs.query.filter_by(mgr_id=mgrid, req_uuid=reqid).first()
        if not reqdata:
            logger.info("Creating new request")
            reqdata = Reqs.query.filter_by(mgr_id=mgrid).first()
            if reqdata:
                creator_name = reqdata.creator_name
            else:
                creator_name = ""
            
            client_name = ""
            progress = request.form.get("progress")
            prog_text = request.form.getlist("progress_text")[::-1]

            reqdata = Reqs(
                req_uuid = reqid,
                mgr_id = mgrid,
                creator_name = creator_name,
                client_name = client_name,
                progress = progress,
                tasks = prog_text
            )

            db.session.add(reqdata)
            db.session.commit()
            logger.info("New request created successfully")

            reqdata = Reqs.query.filter_by(mgr_id=mgrid, req_uuid=reqid).first()

        return render_template("editor.html", reqdata=reqdata)
    
    except Exception as e:
        logger.error(f"Error in reqedit: {str(e)}\n{traceback.format_exc()}")
        return "Error processing request", 500

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {str(e)}\n{traceback.format_exc()}")
    return "An error occurred", 500

if __name__ == "__main__":
    logger.info("Starting Flask application")
    app.run(
        debug=False,
        port=8001,
        host="0.0.0.0",
        ssl_context=(
            "/path/to/cert.pem",
            "/path/to/privkey.pem"
        )
    )
