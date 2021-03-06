# coding=utf-8

from lxml import etree

from pymaltego import exceptions, constants
from pymaltego.entities import XMLObject, Node, Entity, UIMessage


class MaltegoMessage(XMLObject):

    """Maltego message object."""

    def __init__(self):
        """Override initialization."""
        self.entities = []
        self.fields = {}
        self.soft_limit = constants.DEFAULT_SOFT_LIMIT
        self.hard_limit = constants.DEFAULT_HARD_LIMIT
        self.ui_messages = []

    @classmethod
    def from_node(cls, node):
        """Load values from node.

        :param node: `etree.Element` instance.
        :returns: `etree.Element` node.
        """
        if not etree.iselement(node):
            raise ValueError('Is not an `etree.Element` instance.')

        node = node.getchildren()[0]

        if node.tag != 'Maltego{}Message'.format(cls.__name__):
            raise exceptions.MalformedMessageError(
                '{} is invalid MaltegoMessage Type.'.format(node.tag)
            )

        return node

    def to_node(self):
        """Serialize to `etree.Element` instance.

        :returns: `etree.Element` instance.
        """
        node = Node(
            'Maltego{}Message'.format(self.__class__.__name__)
        )

        if self.ui_messages:
            ui_messages = Node('UIMessages', parent=node)
            for message in self.ui_messages:
                ui_messages.append(message.to_node())

        return node

    def to_xml(self, pretty_print=False):
        """Serialize to XML string.

        :param pretty_print (optional): `bool` human-readable XML.
        :returns: `str` XML.
        """
        message = Node('MaltegoMessage')
        message.append(self.to_node())
        return etree.tostring(message, pretty_print=pretty_print)


class TransformRequest(MaltegoMessage):

    """Maltego transform request message object."""

    @classmethod
    def from_xml(cls, xml):
        """Create object from xml.

        :param xml: `str` XML.
        :returns: `messages.TransformRequest` instance.
        """
        return cls.from_node(etree.fromstring(xml))

    @classmethod
    def from_node(cls, node):
        """Load values from node.

        :param node: `etree.Element` instance.
        :returns: `messages.TransformRequest` instance.
        """
        node = super(TransformRequest, cls).from_node(node)

        entity_nodes = node.find('Entities')
        if entity_nodes is None:
            raise exceptions.MalformedMessageError(
                'Request requires "Entities" tag.'
            )

        instance = cls()

        for entity in entity_nodes.getchildren():
            instance.entities.append(Entity.from_node(entity))

        fields = node.find('TransformFields')
        if fields is not None:
            for field in fields.getchildren():
                if 'Name' not in field.attrib:
                    raise exceptions.MalformedMessageError(
                        'No "Name" attribute in Field'
                    )
                name = field.attrib['Name']
                value = field.text and field.text.strip()
                instance.fields[name] = value

        limit = node.find('Limits')
        if limit is not None:
            instance.soft_limit = int(
                limit.attrib.get('SoftLimit', constants.DEFAULT_SOFT_LIMIT)
            )
            instance.hard_limit = int(
                limit.attrib.get('HardLimit', constants.DEFAULT_SOFT_LIMIT)
            )

        return instance


class TransformResponse(MaltegoMessage):

    """Maltego transform response message."""

    def __init__(self, entities, ui_messages=None):
        """Override initialization instance.

        :param entities: `list` `entities.Entity` instances.
        :param ui_messages: `list` UI messages.
        """
        super(TransformResponse, self).__init__()
        self.entities = entities
        self.ui_messages = ui_messages or []

    @classmethod
    def from_node(cls, node):
        """Load values from node.

        :param node: `etree.Element` instance.
        :returns: `messages.TransformResponse` instance.
        """
        node = super(TransformResponse, cls).from_node(node)

        entity_nodes = node.find('Entities')
        if entity_nodes is None:
            raise exceptions.MalformedMessageError(
                'Request requires "Entities" tag.'
            )

        entities = []
        for entity in entity_nodes.getchildren():
            entities.append(Entity.from_node(entity))

        ui_messages = []
        message_nodes = node.find('UIMessages')
        for message in message_nodes.getchildren():
            ui_messages.append(UIMessage.from_node(message))

        return cls(entities, ui_messages)

    def to_node(self):
        """Serialize to `etree.Element` instance.

        :returns: `etree.Element` instance.
        """
        node = super(TransformResponse, self).to_node()

        entities_node = Node('Entities', parent=node)
        for entity in self.entities:
            entities_node.append(entity.to_node())

        return node
