#Declare this outside
subjects_topics = {
        "Science": ["Physics", "Chemistry", "Biology"],
        "History": ["Ancient", "Medieval", "Modern"],
        "Math": ["Algebra", "Geometry", "Calculus"],
        "Technology": ["AI", "Programming", "Cybersecurity"]
    }

#Put this code inside app.context()
for subject_name, topics in subjects_topics.items():
    subject = Subject.query.filter_by(sname=subject_name).first()
    if not subject:
        subject = Subject(sname=subject_name)
        db.session.add(subject)
        db.session.commit()  # Commit to get subject.sid

    for topic_name in topics:
        topic = Topic.query.filter_by(tname=topic_name, sid=subject.sid).first()
        if not topic:
            topic = Topic(tname=topic_name, sid=subject.sid)
            db.session.add(topic)

db.session.commit()
print("Subjects and topics populated successfully.")