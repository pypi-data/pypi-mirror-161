from abc import ABC

gameobjects = set()

class Transform:
    def __init__(self, x=0, y=0, width=0, height=0, scale_x=1, scale_y=1):
        """
        The main transform class for managing gameobjects and positions.
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.scale_x = scale_x
        self.scale_y = scale_y

    @property
    def center(self):
        """
        Returns the `x` and `y` cordinates of the center of the current object.
        """
        x = self.x + (self.width / 2)
        y = self.y + (self.height / 2)

        return x, y

    @property
    def top_corner(self):
        """
        Returns the `x` and `y` cordinates of top-corner of the transform.
        """
        x = self.x - (self.width / 2)
        y = self.y + (self.height / 2)

        return x, y

    @property
    def bottom_corner(self):
        """
        Returns the `x` and `y` cordinates of bottom-corner of the transform.
        """
        x = self.x + (self.width / 2)
        y = self.y - (self.height / 2)

        return x, y

    def is_touching_border(self, x_0: int, x_1: int, y_0: int, y_1: int):
        if self.x <= x_0 or self.x >= x_1 or self.y >= y_0 or self.y <= y_1:
            return True
        return False

    def distance(self, transform):
        """
        Measures the distance between the `x` and `y` cordinates of the transform and the `x` and `y` of the given transform and returns the distance.

        Arguments:
            `transform` | The transform object the `x` and `y` cordinates are compared with.
        """
        distance = ((self.x - transform.x)**2 + (self.y - transform.y)**2)**0.5
        return distance

    def change_position(self, x, y):
        """
        Sets the `x` and `y` cordinates of the current object.
        """
        self.x = x or self.x
        self.y = y or self.y

    def change_dimensions(self, width, height):
        """
        Sets the dimensions of the current object.
        """
        self.width = width or self.width
        self.height = height or self.height

    def change_scale(self, sx, sy):
        """
        Sets the scale of the current object to the `sx` and `sy` arguments.
        """
        self.scale_x = sx + self.scale_x
        self.scale_y = sy + self.scale_y

# GameObject
class AbstractGameObject(ABC):
    def __init__(self, transform: Transform, tags: list = [], name: str = None):
        self.__transform__: Transform = transform or Transform()
        self.__tags__ = tags
        self.__name__ = name

    @property
    def transform(self):
        """
        Returns the transform property of the gameobject.
        """
        return self.__transform__

    @property
    def tags(self):
        """
        Returns the tags of the current gameobject.
        """
        return self.__tags__

    @property
    def name(self):
        """
        Returns the name property of the gameobject.
        """
        return self.__name__

    def update(self):
        """
        Updates the gameobject.
        """
        pass


class GameObject(AbstractGameObject):
    def __init__(self, transform: Transform, tags: list = [], name: str = None, colour: str="#FFFFFF", layer: str = "back"):
        """
        The main gameobject class for creating a gameobject.
        """
        super().__init__(transform=transform, tags=tags, name=name)

        # On screen
        self.started = False

        # Removed from screen
        self.destroyed = False

        self.colour = colour
        self.shape = "rectangle"
        self.layer = layer

    def start(self):
        self.started = True
        gameobjects.add(self)

    def destroy(self):
        self.destroyed = True
        gameobjects.remove(self)

    def set_colour(self, colour: str):
        """
        Sets the colour of the gameobject.
        """
        self.colour = colour


    # Timeline
    # start -> update -> render -> destroy