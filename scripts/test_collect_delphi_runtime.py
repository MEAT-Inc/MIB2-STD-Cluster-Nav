"""Offline allowlist and staging-command checks. Never connects to the car."""
import unittest
from collect_delphi_runtime import select_targets,copy_command
class ScopeTests(unittest.TestCase):
    def test_only_named_regular_files_and_file_links(self):
        entries=[('screen-cda','file',100),('libXSAL.so','link',1),('libscreen.so.1','dir',2),('contacts.db','file',3)]
        self.assertEqual(select_targets('/proc/boot',entries),[('/proc/boot/screen-cda',100),('/proc/boot/libXSAL.so',1)])
    def test_scope_rejected(self):
        with self.assertRaises(ValueError):select_targets('/persistence',[])
    def test_traversal_not_selected(self):
        self.assertEqual(select_targets('/proc/boot',[('../screen-cda','file',100)]),[])
    def test_graphics_directory_included(self):
        self.assertEqual(select_targets('/usr/lib/graphics',[('libscreen.so.1','file',123)]),[('/usr/lib/graphics/libscreen.so.1',123)])
    def test_staging_only_new_ramdisk_destination(self):
        root='/ramdisk/delphi-stage_'+'a'*32
        command,dest=copy_command('/proc/boot/screen-cda',root,0)
        self.assertEqual(command,'cp /proc/boot/screen-cda '+root+'/00_screen-cda')
        self.assertTrue(dest.startswith(root+'/'))
    def test_staging_rejects_other_sources_or_roots(self):
        for source,root in [('/persistence/screen-cda','/ramdisk/delphi-stage_'+'a'*32),('/proc/boot/screen-cda','/extbin/apps'),('/proc/boot/screen-cda;reboot','/ramdisk/delphi-stage_'+'a'*32)]:
            with self.subTest(source=source,root=root):
                with self.assertRaises(ValueError):copy_command(source,root,0)
if __name__=='__main__':unittest.main()
