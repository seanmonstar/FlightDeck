"""
jetpack.management.commands.fix_packages
----------------------------------------

Fix uniqueness (author, name) and empty latest
"""
import commonware

from django.core.management.commands.loaddata import Command as BaseCommand

from jetpack.models import Package, PackageRevision

log = commonware.log.getLogger('f.jetpack')


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        """Get all packages and try to fix them
        """
        packages = Package.objects.all()
        fixed_uniqueness_count = 0
        fixed_latest_count = 0
        fixed_version_count = 0
        deleted_packages_count = 0
        for package in packages:
            if package.fix_uniqueness():
                self.stdout.write('[%s] Package not unique' % package.id_number)
                fixed_uniqueness_count += 1
            latest = package.fix_latest()
            if latest:
                self.stdout.write('[%s] No latest' % package.id_number)
                if isinstance(PackageRevision, latest):
                    fixed_latest_count += 1
                else:
                    deleted_packages_count += 1
            if not latest or isinstance(PackageRevision, latest):
                # otherwise the package is deleted anyway
                version = package.fix_version()
                if version:
                    fixed_version_count += 1

        self.stdout.write("""
Finished fixing packages.
%d uniqueness fixed
%d latest revisions fixed
%d version revisions fixed
%d packages deleted
""" % (fixed_uniqueness_count, fixed_latest_count, fixed_version_count,
    deleted_packages_count))
