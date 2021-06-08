[1mdiff --git a/src/dukop/apps/calendar/management/commands/calendar_fixtures.py b/src/dukop/apps/calendar/management/commands/calendar_fixtures.py[m
[1mindex cea3813..601d2bb 100644[m
[1m--- a/src/dukop/apps/calendar/management/commands/calendar_fixtures.py[m
[1m+++ b/src/dukop/apps/calendar/management/commands/calendar_fixtures.py[m
[36m@@ -194,6 +194,8 @@[m [mclass Command(BaseCommand):[m
                         comment="This is a randomly generated time",[m
                     )[m
 [m
[32m+[m[32m                    event.spheres.add(models.Sphere.get_default())[m
[32m+[m
                     if random.choice([True, False]):[m
                         image_data = random_image(use_local=local_image)[m
                         event_image = models.EventImage(event=event)[m
[1mdiff --git a/src/dukop/apps/calendar/models.py b/src/dukop/apps/calendar/models.py[m
[1mindex 7c5fcd2..c6e99cb 100644[m
[1m--- a/src/dukop/apps/calendar/models.py[m
[1m+++ b/src/dukop/apps/calendar/models.py[m
[36m@@ -18,6 +18,7 @@[m [mfrom dukop.apps.calendar.utils import display_time[m
 from sorl.thumbnail import get_thumbnail[m
 [m
 from . import utils[m
[32m+[m[32mfrom django.utils import timezone[m
 [m
 [m
 def image_upload_to(instance, filename):[m
[36m@@ -359,7 +360,7 @@[m [mclass EventTime(models.Model):[m
         representation = display_datetime(self.start)[m
         if self.end:[m
             if self.end.date() == self.start.date():[m
[31m-                representation += " - {}".format(display_time(self.end[7m.time()[27m))[m
[32m+[m[32m                representation += " - {}".format(display_time(self.end[7m[27m))[m
             else:[m
                 representation += " - {}".format(display_datetime(self.end))[m
         return representation[m
