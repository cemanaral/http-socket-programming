from database.database import Database
import server.server_base


class ActivityServer(server.server_base.ServerBase):
    """
    Activity Database model:
    [
        "activity1",
        "activity2",
        ...
    ]
    """
    activities = Database("activity")

    def add(self, name):
        if name in self.activities.db_object:
            return self.HTTP_403_FORBIDDEN + self.header + f'<h2>Activity {name} already exists!</h2>'
        self.activities.db_object.append(name)
        self.activities.save()
        return self.HTTP_200_OK + self.header + f'<h2>Activity {name} succesfully added!</h2>'

    def remove(self, name):
        if name not in self.activities.db_object:
            return self.HTTP_403_FORBIDDEN + self.header + f'<h2>Activity {name} does not exist!</h2>'
        self.activities.db_object.remove(name)
        self.activities.save()
        return self.HTTP_200_OK + self.header + f'<h2>Activity {name} succesfully removed!</h2>'

    def check(self, name):
        if name in self.activities.db_object:
            return self.HTTP_200_OK + self.header + f'<h2>Activity {name} exists.'
        return self.HTTP_404_NOT_FOUND + self.header + f'<h2>Activity {name} does not exist.'
