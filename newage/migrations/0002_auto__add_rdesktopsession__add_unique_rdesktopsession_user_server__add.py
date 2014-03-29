# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'RdesktopSession'
        db.create_table(u'newage_rdesktopsession', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now)),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime.now)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['newage.RdesktopUser'])),
            ('server', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['newage.TerminalServer'])),
            ('fullscreen', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('geometry', self.gf('django.db.models.fields.CharField')(max_length=15, blank=True)),
            ('printer_queues_raw', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('smartcard_raw', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'newage', ['RdesktopSession'])

        # Adding unique constraint on 'RdesktopSession', fields ['user', 'server']
        db.create_unique(u'newage_rdesktopsession', ['user_id', 'server_id'])

        # Adding model 'RdesktopUser'
        db.create_table(u'newage_rdesktopuser', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now)),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime.now)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('username', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30)),
        ))
        db.send_create_signal(u'newage', ['RdesktopUser'])

        # Adding model 'SambaDomain'
        db.create_table(u'newage_sambadomain', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now)),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime.now)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal(u'newage', ['SambaDomain'])

        # Adding model 'Server'
        db.create_table(u'newage_server', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now)),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime.now)),
            ('hostname', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('fqdn', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('ip_address', self.gf('django.db.models.fields.GenericIPAddressField')(max_length=39, null=True, blank=True)),
            ('samba_domain', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['newage.SambaDomain'], null=True, blank=True)),
        ))
        db.send_create_signal(u'newage', ['Server'])

        # Adding model 'TerminalServer'
        db.create_table(u'newage_terminalserver', (
            (u'server_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['newage.Server'], unique=True, primary_key=True)),
        ))
        db.send_create_signal(u'newage', ['TerminalServer'])


    def backwards(self, orm):
        # Removing unique constraint on 'RdesktopSession', fields ['user', 'server']
        db.delete_unique(u'newage_rdesktopsession', ['user_id', 'server_id'])

        # Deleting model 'RdesktopSession'
        db.delete_table(u'newage_rdesktopsession')

        # Deleting model 'RdesktopUser'
        db.delete_table(u'newage_rdesktopuser')

        # Deleting model 'SambaDomain'
        db.delete_table(u'newage_sambadomain')

        # Deleting model 'Server'
        db.delete_table(u'newage_server')

        # Deleting model 'TerminalServer'
        db.delete_table(u'newage_terminalserver')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'newage.rdesktopsession': {
            'Meta': {'ordering': "(u'user__username',)", 'unique_together': "((u'user', u'server'),)", 'object_name': 'RdesktopSession'},
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'fullscreen': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'geometry': ('django.db.models.fields.CharField', [], {'max_length': '15', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'printer_queues_raw': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'server': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['newage.TerminalServer']"}),
            'smartcard_raw': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['newage.RdesktopUser']"})
        },
        u'newage.rdesktopuser': {
            'Meta': {'ordering': "(u'username',)", 'object_name': 'RdesktopUser'},
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'newage.sambadomain': {
            'Meta': {'ordering': "(u'name',)", 'object_name': 'SambaDomain'},
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'newage.server': {
            'Meta': {'ordering': "(u'fqdn',)", 'object_name': 'Server'},
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'fqdn': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'hostname': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.GenericIPAddressField', [], {'max_length': '39', 'null': 'True', 'blank': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'samba_domain': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['newage.SambaDomain']", 'null': 'True', 'blank': 'True'})
        },
        u'newage.terminalserver': {
            'Meta': {'ordering': "(u'fqdn',)", 'object_name': 'TerminalServer', '_ormbases': [u'newage.Server']},
            u'server_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['newage.Server']", 'unique': 'True', 'primary_key': 'True'})
        }
    }

    complete_apps = ['newage']