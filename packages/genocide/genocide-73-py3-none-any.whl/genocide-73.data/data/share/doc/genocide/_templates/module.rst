.. _{{ name }}:

.. raw:: html

    <br><br>
    <center><b>


{{ name }}
{{ underline }}

.. raw:: html

    </b>
    </center>
    <br>

.. automodule:: {{ fullname }}
    :members:

    {% block exceptions %}
    {% if exceptions %}
    .. rubric:: exceptions

    .. autosummary::
    {% for item in exceptions %}
        {{ item }}
    {%- endfor %}
    {% endif %}
    {% endblock %}


    {% block classes %}
    {% if classes %}
    .. rubric:: classes

    .. autosummary:: 
    {% for item in classes %}
        {{ item }}
    {%- endfor %}
    {% endif %}
    {% endblock %}

    {% block functions %}
    {% if functions %}
    .. rubric:: functions

    .. autosummary::
    {% for item in functions %}
        {{ item }}
    {%- endfor %}
    {% endif %}
    {% endblock %}

    .. raw:: html

       <br><br>


.. raw:: html

    <br>
    <center><b>
    
:ref:`home <home>` - :ref:`reconsider <reconsider>` - :ref:`request <request>` - :ref:`evidence <evidence>` - :ref:`guilty <guilty>` - :ref:`writings <writings>` - :ref:`manual <man>` :ref:`\! <source>`


.. raw:: html

    </b></center>
