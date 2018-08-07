import chainer


class LinkHook(object):
    """Base class of hooks for Links.

    :class:`~chainer.LinkHook` is a callback object
    that is registered to a :class:`~chainer.Link`.
    Registered link hooks are invoked before and after calling
    :meth:`Link.forward() <chainer.Link.forward>` method of each link.

    Link hooks that derive from :class:`LinkHook` may override the following
    method:

    * :meth:`~chainer.LinkHook.added`
    * :meth:`~chainer.LinkHook.deleted`
    * :meth:`~chainer.LinkHook.forward_preprocess`
    * :meth:`~chainer.LinkHook.forward_postprocess`

    By default, these methods do nothing.

    Specifically, when :meth:`~chainer.Link.__call__`
    method of some link is invoked,
    :meth:`~chainer.LinkHook.forward_preprocess`
    (resp. :meth:`~chainer.LinkHook.forward_postprocess`)
    of all link hooks registered to this link are called before (resp. after)
    :meth:`Link.forward() <chainer.Link.forward>` method of the link.

    There are two ways to register :class:`~chainer.LinkHook`
    objects to :class:`~chainer.Link` objects.

    First one is to use ``with`` statement. Link hooks hooked
    in this way are registered to all links within ``with`` statement
    and are unregistered at the end of ``with`` statement.

    .. admonition:: Example

        The following code is a simple example in which
        we measure the elapsed time of a part of forward propagation procedure
        with :class:`~chainer.link_hooks.TimerHook`, which is a subclass of
        :class:`~chainer.LinkHook`.

        >>> class Model(chainer.Chain):
        ...   def __init__(self):
        ...     super(Model, self).__init__()
        ...     with self.init_scope():
        ...       self.l = L.Linear(10, 10)
        ...   def forward(self, x1):
        ...     return F.exp(self.l(x1))
        >>> model1 = Model()
        >>> model2 = Model()
        >>> x = chainer.Variable(np.zeros((1, 10), np.float32))
        >>> with chainer.link_hooks.TimerHook() as m:
        ...   _ = model1(x)
        ...   y = model2(x)
        >>> model3 = Model()
        >>> z = model3(y)
        >>> print('Total time : {}'.format(m.total_time()))
        ... # doctest:+ELLIPSIS
        Total time : ...

        In this example, we measure the elapsed times for each forward
        propagation of all links in ``model1`` and ``model2``
        (specifically, :class:`~chainer.links.Linear` and ``Model``).
        Note that ``model3`` is not a target of measurement
        as :class:`~chainer.link_hooks.TimerHook` is unregistered
        before forward propagation of ``model3``.

    .. note::

       Chainer stores the dictionary of registered link hooks
       as a thread local object. So, link hooks registered
       are different depending on threads.

    The other one is to register directly to
    :class:`~chainer.Link` object with
    :meth:`~chainer.Link.add_hook` method.
    Link hooks registered in this way can be removed by
    :meth:`~chainer.Link.delete_hook` method.
    Contrary to former registration method, link hooks are registered
    only to the link which :meth:`~chainer.Link.add_hook`
    is called.

    Args:
        name(str): Name of this link hook.
    """

    name = 'LinkHook'

    def __enter__(self):
        link_hooks = chainer._get_link_hooks()
        if self.name in link_hooks:
            raise KeyError('hook %s already exists' % self.name)

        link_hooks[self.name] = self
        self.added(None)
        return self

    def __exit__(self, *_):
        link_hooks = chainer._get_link_hooks()
        link_hooks[self.name].deleted(None)
        del link_hooks[self.name]

    def added(self, link):
        """Callback function invoked when the link hook is registered

        Args:
            link(~chainer.Link): Link object to which
                the link hook is registered. ``None`` if the link hook is
                registered globally.
        """
        pass

    def deleted(self, link):
        """Callback function invoked when the link hook is unregistered

        Args:
            link(~chainer.Link): Link object to which
                the link hook is unregistered. ``None`` if the link hook had
                been registered globally.
        """
        pass

    # forward
    def forward_preprocess(self, args):
        """Callback function invoked before a forward call of a link.

        Args:
            args: Callback data. It has the following attributes:

                * link (:class:`~chainer.Link`)
                    Link object.
                * forward_method (:class:`str`)
                    Name of the forward method.
                * args (:class:`tuple`)
                    Non-keyword arguments given to the forward method.
                * kwargs (:class:`dict`)
                    Keyword arguments given to the forward method.
        """
        pass

    def forward_postprocess(self, args):
        """Callback function invoked after a forward call of a link.

        Args:
            args: Callback data. It has the following attributes:

                * link (:class:`~chainer.Link`)
                    Link object.
                * forward_method (:class:`str`)
                    Name of the forward method.
                * args (:class:`tuple`)
                    Non-keyword arguments given to the forward method.
                * kwargs (:class:`dict`)
                    Keyword arguments given to the forward method.
                * out
                    Return value of the forward method.
        """
        pass
