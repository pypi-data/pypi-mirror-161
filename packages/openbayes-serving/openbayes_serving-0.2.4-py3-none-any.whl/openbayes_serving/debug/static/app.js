document.addEventListener("DOMContentLoaded", event => {
  const url = window.location.pathname;
  const traceId = +url.split('/').pop();
  const titleEl = document.querySelector('.title');
  const descriptionEl = document.querySelector('.description');
  const tracebackEl = document.querySelector('.traceback');
  const plaintextEl = document.querySelector('.plaintext');

  function activeContainers(params) {
    document.querySelector('.main').classList.add('active');
    document.querySelector('.loading').classList.remove('active');
  }

  console.log(`current traceback id: ${traceId}`);
  if (Number.isInteger(traceId)) {
    fetch(`../traceback/${traceId}`, {
      mode: 'no-cors'
    })
    .then(response => {
      if (!response.ok) {
        titleEl.textContent = `Exception not found`
        descriptionEl.textContent = `Cannot find trace ID #${traceId}.`
        activeContainers();
        plaintextEl.remove();
        throw new Error('Response not ok');
      }
      return response.json();
    })
    .then(data => {
      // Update title
      const exceptionTitle = data.exception;
      const exceptionType = data.exception_type;
      const exceptionGroups = data.groups;

      // Update basic content
      document.title = `${exceptionTitle} #${traceId} - OpenBayes Serving Debugger`
      titleEl.textContent = exceptionType;
      descriptionEl.textContent = exceptionTitle;

      // Update plain traceback
      plaintextEl.querySelector('pre').textContent = data.plaintext;
      hljs.highlightBlock(plaintextEl.querySelector('pre'));

      // Update traceback
      const groupTemplate = document.querySelector('#group');
      const frameTemplate = document.querySelector('#frame');
      const contextTemplate = document.querySelector('#context');
      const consoleOutputTemplate = document.querySelector('#console-output');

      exceptionGroups.forEach(group => {
        const groupEl = groupTemplate.content.firstElementChild.cloneNode(true);
        const frames = group.frames;

        frames.forEach(frame => {
          // Let's work on `HTMLDivElement` instead of `DocumentFragment`
          const frameEl = frameTemplate.content.firstElementChild.cloneNode(true);
          const contexts = frame.context;
          let highlightedLine = '';

          contexts.forEach(context => {
            const contextEl = contextTemplate.content.firstElementChild.cloneNode(true);

            contextEl.querySelector('.line').textContent = `${context.line}`;
            hljs.highlightBlock(contextEl.querySelector('.line'));

            // Highlight selected line defined from parent
            if (frame.lineno === context.lineno) {
              highlightedLine = context.line;
              contextEl.classList.add('active');
            }
            frameEl.querySelector('.contexts-wrap').appendChild(contextEl);
          })

          frameEl.setAttribute('id', frame.id);
          frameEl.querySelector('.contexts-wrap').setAttribute('start', contexts[0].lineno);
          frameEl.setAttribute('highlight', frame.lineno);
          frameEl.querySelector('.highlighted-exception').textContent = highlightedLine;
          hljs.highlightBlock(frameEl.querySelector('.highlighted-exception'));
          frameEl.querySelector('.filename').textContent = frame.filename;
          frameEl.querySelector('.filename').title = frame.realpath;
          frameEl.querySelector('.function').textContent = frame.function;
          frameEl.querySelector('.lineno').textContent = frame.lineno;
          frameEl.querySelector('.expanded-summary-content.filename').textContent = frame.realpath;
          groupEl.querySelector('.frames-wrap').appendChild(frameEl);
          frame.is_library && frameEl.querySelector('.is-library').classList.add('on');

          // Set execution form
          const formEl = frameEl.querySelector('.textarea');
          if (formEl) {
            formEl.addEventListener('keydown', () => {
              let padding = parseFloat(window.getComputedStyle(formEl, null).getPropertyValue('padding-top'));

              setTimeout(() => {
                formEl.style.cssText = 'height: auto';
                formEl.style.cssText = 'height: ' + (formEl.scrollHeight - padding * 2) + 'px';
              }, 0);
            })

            formEl.addEventListener('keypress', e => {
              if (e.keyCode === 13 && !e.shiftKey) {
                e.preventDefault();

                const inputValue = formEl.value ? formEl.value : '';
                formEl.setAttribute('disabled', true);

                fetch(`../frame/${frame.id}/exec`, {
                  body: JSON.stringify({'code': inputValue}),
                  headers: {
                    'Content-Type': 'application/json',
                  },
                  method: 'post'
                })
                .then(response => {
                  if (!response.ok) {
                    throw new Error('POST Response not ok');
                  }
                  return response.json();
                })
                .then(data => {
                  const consoleOutputEl = consoleOutputTemplate.content.firstElementChild.cloneNode(true);
                  consoleOutputEl.querySelector('.prompt').textContent = '>>>';

                  // Update content
                  consoleOutputEl.querySelector('.input').textContent = data.code;
                  hljs.highlightBlock(consoleOutputEl.querySelector('.input'));

                  if (data.traceback) {
                    consoleOutputEl.querySelector('.output').textContent = data.traceback.plaintext;
                    consoleOutputEl.classList.add('error');
                  } else {
                    consoleOutputEl.querySelector('.output').textContent = data.output;
                    formEl.value = '';
                  }

                  hljs.highlightBlock(consoleOutputEl.querySelector('.output'));
                  frameEl.querySelector('.console-outputs').appendChild(consoleOutputEl);

                  // Scroll to the buttom of the outputs container
                  frameEl.querySelector('.console-outputs').scrollTop = frameEl.querySelector('.console-outputs').scrollHeight;

                  // Reset console input state
                  formEl.removeAttribute('disabled');
                  formEl.focus();
                })
              }
            });
          }
        })

        groupEl.querySelector('.exception .content').textContent = `${group.exception}`

        // Update relations
        let groupTitle = '';
        if (group.relation === 'root') {
          // Traceback (most recent call last)
          groupTitle = '异常追溯（最近一次）';
        } else if (group.relation === 'cause') {
          // The above exception was the direct cause of the following exception:
          groupTitle = '上述异常是造成以下异常的直接原因：';
        } else if (group.relation === 'context') {
          // During handling of the above exception, another exception occurred:
          groupTitle = '在处理上述异常期间，发生了另一个异常：';
        } else {
          groupTitle = 'Error';
        }
        groupEl.querySelector('h2').textContent = groupTitle;
        groupEl.setAttribute('relation', `${group.relation}`);

        // Returns all elements
        tracebackEl.appendChild(groupEl);
      });

      // Active containers
      activeContainers();
    })
    .catch(error => {
      console.error('Error:', error);
    });
  } else {
    titleEl.textContent = `Invalid trace ID`
    descriptionEl.textContent = `The trace ID you provided is invalid.`
    activeContainers();
    plaintextEl.remove();
  }
});
