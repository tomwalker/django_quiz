# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'MCQuestion'
        db.create_table(u'multichoice_mcquestion', (
            (u'question_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['quiz.Question'], unique=True, primary_key=True)),
        ))
        db.send_create_signal(u'multichoice', ['MCQuestion'])

        # Adding model 'Answer'
        db.create_table(u'multichoice_answer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['multichoice.MCQuestion'])),
            ('content', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('correct', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'multichoice', ['Answer'])


    def backwards(self, orm):
        # Deleting model 'MCQuestion'
        db.delete_table(u'multichoice_mcquestion')

        # Deleting model 'Answer'
        db.delete_table(u'multichoice_answer')


    models = {
        u'multichoice.answer': {
            'Meta': {'object_name': 'Answer'},
            'content': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'correct': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['multichoice.MCQuestion']"})
        },
        u'multichoice.mcquestion': {
            'Meta': {'ordering': "['category']", 'object_name': 'MCQuestion', '_ormbases': [u'quiz.Question']},
            u'question_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['quiz.Question']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'quiz.category': {
            'Meta': {'object_name': 'Category'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '250', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'quiz.question': {
            'Meta': {'ordering': "['category']", 'object_name': 'Question'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['quiz.Category']", 'null': 'True', 'blank': 'True'}),
            'content': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'explanation': ('django.db.models.fields.TextField', [], {'max_length': '2000', 'blank': 'True'}),
            'figure': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'quiz': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['quiz.Quiz']", 'symmetrical': 'False', 'blank': 'True'}),
            'sub_category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['quiz.SubCategory']", 'null': 'True', 'blank': 'True'})
        },
        u'quiz.quiz': {
            'Meta': {'object_name': 'Quiz'},
            'answers_at_end': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['quiz.Category']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'exam_paper': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'fail_text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_questions': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'pass_mark': ('django.db.models.fields.SmallIntegerField', [], {'default': '0', 'blank': 'True'}),
            'random_order': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'single_attempt': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'success_text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'url': ('django.db.models.fields.SlugField', [], {'max_length': '60'})
        },
        u'quiz.subcategory': {
            'Meta': {'object_name': 'SubCategory'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['quiz.Category']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sub_category': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['multichoice']