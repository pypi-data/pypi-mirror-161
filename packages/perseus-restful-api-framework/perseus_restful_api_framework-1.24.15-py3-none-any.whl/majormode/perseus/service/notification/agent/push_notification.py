#!/usr/bin/env python
#
# Copyright (C) 2019 Majormode.  All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# from majormode.perseus.model.obj import OBJECT_STATUS_DELETED
# from majormode.perseus.model.obj import OBJECT_STATUS_ENABLED
# from majormode.perseus.model.obj import OBJECT_STATUS_PENDING
# from majormode.perseus.model.obj import Object
# from majormode.perseus.service.notification.notification_service import NotificationService
#
# from majormode.utils import cast
# from majormode.utils.agent import AbstractAgent
# from majormode.utils.date_util import ISO8601DateTime
# from majormode.utils.rdbms import RdbmsConnection
#
# import argparse
# import blist
# import datetime
# import os
# import settings
# import sys
# import threading
# import time
# import traceback
#
#
# PUSH_NOTIFICATION_BATCH_SIZE = 100
#
# # Define the default number of worker threads that will be used to
# # process new photos that have been captured and uploaded to the local
# # server box.
# DEFAULT_WORKER_POOL_SIZE = 1
#
#
# class PushNotificationController(AbstractAgent):
#     # Semaphore to protect concurrent accesses to the queue of push
#     # notification notifications from worker threads.
#     SEMAPHORE_NOTIFICATIONS = threading.Semaphore()
#
#     NOTIFICATION_SERVICE = NotificationService()
#
#     # Queue of ``PushNotification` instances corresponding to
#     # notifications which need to be sent to a particular device as soon as
#     # possible or in a close future according to its schedule time.
#     # These notifications are sorted in their ascending order of schedule time;
#     # notifications with no schedule time defined come first (as a fortunate
#     # consequence of comparing `None` with an object non-null).
#     notifications = blist.sortedset(key=lambda x: x.schedule_time)
#
#
#     class __PushNotificationAgent__(AbstractAgent):
#         """
#         Class responsible for pushing at a given time one notification to one
#         device, independently from other workers.
#         """
#         def __init__(self):
#             """
#             Build a ``__PushNotificationAgent__`` instance.
#             """
#             super(PushNotificationController.__PushNotificationAgent__, self).__init__()
#             self.notification = None
#
#         def do(self):
#             if self.notification is None:
#                 return False
#
#             try:
#                 _notification_ = Object(
#                         creation_time=self.notification.creation_time,
#                         notification_id=self.notification.notification_id,
#                         notification_type=self.notification.notification_type,
#                         payload=self.notification.payload,
#                         schedule_time=self.notification.schedule_time,
#                         sender_id=self.notification.sender_id)
#
#                 if self.notification.device_platform == 'ios':
#                     PushNotificationController.NOTIFICATION_SERVICE._push_notification_to_ios(
#                             self.notification.device_token,
#                             alert=_notification_)
#
#                 elif self.notification.device_platform == 'android':
#                     PushNotificationController.NOTIFICATION_SERVICE._push_android_notification(
#                             settings.GCM_API_KEY,
#                             self.notification.device_token,
#                             _notification_,
#                             #delay_while_idle=True, # Indicate that the message should not be sent until the device becomes active.
#                             time_to_live=self.notification.time_to_live)
#
#                 sys.stdout.write('#') ; sys.stdout.flush()
#
#                 self.notification = None
#
#             except:
#                 print traceback.format_exc()
#
#             return True
#
#
#         def is_available(self):
#             """
#             Indicate whether this worker is available for pushing a notification to a
#             device.
#
#             @return: ``True`` if this worker is not pushing any notification to a
#                 device; ``False`` if this worker is still processing a push
#                 notification to a device.
#             """
#             return self.is_enabled() and self.notification is None
#
#
#         def set_notification(self, notification):
#             """
#             Set the notification that this worker is requested to push to a device.
#
#             @param notification: a ``PushNotification`` instance corresponding
#                 to a notification to push to a device as indicated in this instance.
#             """
#             if self.notification is not None:
#                 raise Exception('This worker is still sending a push notification notification.')
#
#             self.notification = notification
#
#
#     def __init__(self, worker_pool_size=DEFAULT_WORKER_POOL_SIZE):
#         """
#         Build ``PushNotificationController`` instance.
#
#         @param worker_pool_size: number of workers to instantiate.
#         """
#         super(PushNotificationController, self).__init__()
#
#         self.worker_pool = [ PushNotificationController.__PushNotificationAgent__()
#                 for i in range(worker_pool_size) ]
#
#         for worker in self.worker_pool:
#             worker.start()
#
#
#     @staticmethod
#     def add_notifications(notifications):
#         """
#         Add the given notifications to be pushed to the specified devices.
#
#         @param notifications: a list of notification notification instances to push to
#             registered devices.
#         """
#         with PushNotificationController.SEMAPHORE_NOTIFICATIONS:
#             PushNotificationController.notifications.update(notifications)
#
#
#     def do(self):
#         with PushNotificationController.SEMAPHORE_NOTIFICATIONS:
#             notification_count = len(PushNotificationController.notifications)
#             if notification_count == 0:
#                 return False
#
#             available_agents = [ agent for agent in self.worker_pool if agent.is_available() ]
#
#             for i in range(min(len(available_agents), notification_count)):
#                 notification = PushNotificationController.notifications[0]
#                 if notification.schedule_time and notification.schedule_time > ISO8601DateTime.now():
#                     return i > 0
#
#                 available_agents[i].set_notification(PushNotificationController.notifications.pop())
#
#         return True
#
#
#     def shutdown(self):
#         for worker in self.worker_pool:
#             worker.shutdown()
#
#         super(PushNotificationController, self).shutdown()
#
#
# def fetch_notifications(rdbms_connection_properties,
#         batch_size=PUSH_NOTIFICATION_BATCH_SIZE):
#     with RdbmsConnection.acquire_connection(rdbms_connection_properties, auto_commit=True) as connection:
#
#         # Retrieve a list of notifications that need to be pushed to one or more
#         # devices, sorted by their schedule time in ascending order.
#         cursor = connection.execute("""
#             SELECT notification_id,
#                    notification_type,
#                    recipient_id,
#                    device_token,
#                    device_platform,
#                    sender_id,
#                    payload,
#                    utc_offset,
#                    schedule_time,
#                    expiration_time,
#                    use_local_time,
#                    notification.app_id,
#                    notification.creation_time
#                 FROM notification,
#                      notification_device
#                 WHERE notification.object_status = %(OBJECT_STATUS_ENABLED)s
#                   AND notification_mode = %(NOTIFICATION_MODE_PUSH)s
#                   AND (notification.recipient_id = notification_device.account_id::text OR
#                        notification.recipient_id = notification_device.device_id)
#                   -- AND notification.package = notification_device.package
#                   AND notification_device.object_status = %(OBJECT_STATUS_ENABLED)s
#                   AND (schedule_time IS NULL OR
#                        (NOT use_local_time AND schedule_time <= current_timestamp) OR
#                        (use_local_time AND schedule_time >= current_timestamp - '12 hours'::interval AND schedule_time < current_timestamp + '12 hours'::interval))
#                   AND is_broadcast = false -- DOES NOT SUPPORT BROADCASTING YET!
#                 ORDER BY schedule_time ASC NULLS FIRST,
#                          notification.creation_time ASC
#                 LIMIT %(limit)s
#                 FOR UPDATE""",
#             { 'NOTIFICATION_MODE_PUSH': NotificationService.NotificationMode.push,
#               'OBJECT_STATUS_ENABLED': OBJECT_STATUS_ENABLED,
#               'limit': batch_size})
#
#         notifications = [ row.get_object({
#                 'app_id': cast.string_to_uuid,
#                 'creation_time': cast.string_to_timestamp,
#                 'expiration_time': cast.string_to_timestamp,
#                 'notification_id': cast.string_to_uuid,
#                 'schedule_time': cast.string_to_timestamp })
#             for row in cursor.fetch_all() ]
#
#         if notifications:
#             connection.execute("""
#                 UPDATE notification
#                   SET object_status = %(OBJECT_STATUS_PENDING)s
#                   WHERE notification_id IN (%[notification_ids]s)""",
#                 { 'OBJECT_STATUS_PENDING': OBJECT_STATUS_PENDING,
#                   'notification_ids': set([ notification.notification_id for notification in notifications ]) })
#
#             # Convert the schedule and the expiration times to UTC if they were
#             # given in local time to the device.
#             #
#             # @todo: broadcast is not yet supported. There will be then one
#             #     notification per device, each device has its own time zone.
#             for notification in notifications:
#                 if notification.schedule_time and notification.use_local_time:
#                     notifications.schedule_time -= datetime.timedelta(hours=notification.utc_offset)
#
#                 if notification.expiration_time and notification.use_local_time:
#                     notification.expiration_time =- datetime.timedelta(hours=notification.utc_offset)
#
#                 notification.time_to_live = notification.expiration_time and \
#                         (notification.expiration_time - ISO8601DateTime.now()).total_seconds()
#
#         # Filter out notifications that have already expired.
#         return [ notification for notification in notifications
#                 if notification.time_to_live is None or notification.time_to_live > 0 ]
#
#
# def main(worker_pool_size):
#     push_notification_controller = PushNotificationController(worker_pool_size=worker_pool_size)
#     push_notification_controller.start()
#
#     try:
#         while True:
#             notifications = fetch_notifications(settings.RDBMS_CONNECTION_PROPERTIES,
#                     batch_size=PUSH_NOTIFICATION_BATCH_SIZE)
#             if len(notifications) > 0:
#                 push_notification_controller.add_notifications(notifications)
#
#             time.sleep(1)
#
#     except KeyboardInterrupt:
#         pass
#
#     except Exception, exception:
#         print traceback.format_exc()
#
#     finally:
#         push_notification_controller.shutdown()
#
#     print
#
#
# if __name__ == "__main__":
#     print "Push Notification Agent"
#     print "Copyright (C) 2013 Majormode.  All rights reserved."
#
#     parser = argparse.ArgumentParser(description='Background task used to push notifications to devices')
#     parser.add_argument('--workers', required=False, default=DEFAULT_WORKER_POOL_SIZE)
#     arguments = parser.parse_args()
#
#     main(arguments.workers)
