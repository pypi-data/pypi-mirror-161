let ElementaryFlask = {
    privateSubmitForm: function (frm, action, body, headers = null) {
        fetch(action, {
            method: 'POST',
            headers: headers,
            body: body,
        })
            .then(response => response.json())
            .then(data => {
                ElementaryFlask.formResponse(data, frm);

            })
            .catch((error) => {
                console.error('Error:', error);
                ElementaryFlask.toast(error);
            });
    },
    submitForm: async function (frm) {
        ElementaryFlask.privateSubmitForm(frm, frm.action, new FormData(frm))
    },
    submitFormEx1: async function (frm,
                                   {
                                       action = undefined,
                                       data = undefined,
                                       body = undefined,
                                       headers = undefined,
                                       submit = undefined,
                                   }) {
        const has_submit = submit !== undefined && submit !== null;

        if ((frm === null || frm === undefined) && has_submit) {
            frm = submit.closest('form');
        }
        if (typeof action === 'undefined')
            action = frm.getAttribute('action');


        if (typeof body === 'undefined') {
            if (typeof data === 'undefined')
                data = ElementaryFlask.formDataToObject(new FormData(frm));
            if (has_submit) {
                // if(submit.value === undefined)
                // data[submit.name] = submit.value;
                data[submit.getAttribute('name')] = submit.getAttribute('value');
            }
            body = JSON.stringify(data);
        }

        if (typeof headers === 'undefined')
            headers = {"Content-Type": "application/json", "Accept": "application/json"};


        ElementaryFlask.privateSubmitForm(frm, action, body, headers);
        return false;
    },
    formDataToObject: function (frmData) {
        // console.log(frmData);
        let object = {};
        frmData.forEach((value, key) => {
            // Reflect.has in favor of: object.hasOwnProperty(key)
            if (!Reflect.has(object, key)) {
                object[key] = value;
                return;
            }
            if (!Array.isArray(object[key])) {
                object[key] = [object[key]];
            }
            object[key].push(value);
        });
        // console.log(object, Object.fromEntries(frmData.entries()));
        return object;
        // return JSON.stringify(object);
    },

    listingCheckboxClick: function (el) {
        el.querySelector("input[type=checkbox]").click();
    },

    submitListingAction: async function (button, frm_id = null) {
        // let frm = document.getElementById(frm_id);
        // let data = ElementaryFlask.serializeForm(frm);
        if (document.getSelection().type == 'Range') {
            return null;
        }
        let frm = button.form;

        if (!frm) {
            if (frm_id) {
                frm = document.getElementById(frm_id);
            } else {
                frm = button.closest("form");
            }
        }

        let frmData = new FormData(frm);
        let button_info = JSON.parse(button.dataset.info);
        if (button_info.action === null) {
            return null;
        }
        let ids = Array();

        if (button_info.item_id === 'batch') {
            if (!frmData.has('id')) {
                return null;
            }
            ids = frmData.getAll('id');

        } else {
            ids.push(button_info.item_id);
        }
        // frmData = FormData();
        for (const id_ of ids) {
            frmData.append("ids", id_);
        }
        frmData.append("action", button_info.action);
        frmData.delete("id");
        return ElementaryFlask.privateSubmitForm(null, frm.action, frmData);

    },

    serializeForm: function (frm, doseq = true) {
        return ElementaryFlask.serializeFormData(new FormData(frm));

    },

    serializeFormData: function (formData, doseq = true) {
        let object = {};
        formData.forEach(function (value, key) {
            if (!(key in object && doseq)) {
                object[key] = value;
            } else {
                if (!Array.isArray(object[key])) {
                    object[key] = Array(object[key]);
                }
                object[key].push(value);

            }
        });
        return object;
    },

    formResponse: function (formResponseData, frm = null, el = null) {
        // console.log(data);
        for (formAction of formResponseData.actions) {
            switch (formAction.action) {
                case 'toast':
                    ElementaryFlask.toast(
                        formAction.params.message,
                        formAction.params.message_type,
                        formAction.params.message_title,
                        formAction.params.sticky,
                        formAction.params.timeout,
                    );
                    break;
                case 'redirect':
                    ElementaryFlask.redirect(formAction.params.destination);
                    break;
                case 'refresh':
                    ElementaryFlask.refresh_page();
                    break;
                case 'replace':
                    if (frm === null) {
                        console.error("Stateless element is not set!");
                        throw "Stateless element is not set!";
                    }
                    ElementaryFlask.replaceElement(frm, formAction.params.html);
                    break;
                case 'hide':
                    if (frm === null) {
                        console.error("Stateless element is not set!");
                        throw "Stateless element is not set!";
                    }
                    ElementaryFlask.hideElement(frm, formAction.params.selector,
                        formAction.params.select_from_document, formAction.params.closest);
                    break;
                case 'dom_element_manipulation':
                    ElementaryFlask.elementManipuation(
                        frm, formAction.params);
                    break;
                case 'eval':
                    eval(formAction.params.code);
                    break;
                case 'state':
                    if (el === null) {
                        console.error("Stateful element is not set!");
                        throw "Stateful element is not set!";
                    }
                    ElementaryFlask.updateState(el, formAction.params.new_state);

            }
        }
    },

    toast: function (msg, type = 'error', title = '', sticky = false, timeout = 10) {
        // check if AdminLTE Toasts exists: # TODO replace with more generic toast plugin
        if (typeof $(document).Toasts == 'function')
            return ElementaryFlask._adminlte_toast(msg, type, title, sticky, timeout)

        alert(msg);
    },
    _adminlte_toast: function (msg, type = 'error', title = 'Error',
                               sticky = true, timeout = 10) {
        let icon = null;
        switch (type) {
            case 'error':
                icon = "fas fa-exclamation-circle text-danger";
                break;
            case 'warning':
                icon = "fas fa-exclamation-triangle text-warning";
                break;
            case 'success':
                icon = "fas fa-check-circle text-success";
                break;
            case 'info':
                icon = "fas fa-info-circle text-info";
                break;
        }
        if (msg.length < 50) {
            msg += '&nbsp;'.repeat(50 - msg.length);
        }
        $(document).Toasts('create', {
            title: title,
            body: msg,
            icon: icon,
            autohide: !sticky,
            delay: !sticky ? timeout * 1000 : null
        });

    },

    redirect: function (dst) {
        // window.location.replace(dst);
        window.location.href = dst;
    },

    refresh_page: function () {
        // window.location.replace(dst);
        window.location.reload();
    },

    replaceElement: function (el, new_content) {
        // document.open();
        // document.write(new_content);
        // document.close();
        el.outerHTML = new_content;

    },
    elementManipuation: function (frm, params) {
        let source_element = params.select_from_document ? document : frm;

        let match_elements = frm;
        switch (params.selector_type) {
            case 'closest':
                match_elements = [frm.closest(params.selector)];
                break;
            case 'by_class':
                match_elements = source_element.getElementsByClassName(params.selector);
                break;
            case 'query_selector':
                match_elements = source_element.querySelectorAll(params.selector);
                break;
            case 'by_id':
            default:
                match_elements = [document.getElementById(params.selector)];
                break;

        }

        // console.log(frm, match_elements);
        for (let ei in match_elements) {
            let element = match_elements[ei];
            for (let mi in params.manipulations) {
                let manip = params.manipulations[mi];
                // TODO: check target & action compatibility
                let target = element;
                switch (manip.target) {
                    case 'class':
                        target = element.classList;
                        break;
                    case 'attributes': // TODO: setAttribute
                        target = element.attributes;
                        break;
                    case 'styles':
                        target = element.style;
                        break;
                    case 'parent':
                        target = element.parentElement;
                        break;
                    case 'document':
                        target = document;
                        break;
                    // case 'self':
                    // default:
                    //     target = element;
                    //     break;
                }

                switch (manip.action_type) {
                    case 'extend':
                        target.push(...manip.args)
                        break;
                    case 'update':
                        ElementaryFlask.updateDict(target, manip.args[0])
                        break;
                    case 'remove':
                        target.remove();
                        break;
                    case 'clear':
                        ElementaryFlask.privateClearTarget(target, manip.target);
                        while (target.length > 0) {
                            target.pop();
                        }
                        // TODO: mapping (attributes)
                        break;
                    case 'affect':
                        ElementaryFlask.privateClearTarget(target, manip.target);
                        ElementaryFlask.privateUpdateTarget(target, manip.target, manip.args);
                        break;
                    case 'replace':
                        target.outerHTML = manip.args[0];
                        break;
                    case 'insert':
                        element.insertAdjacentHTML(manip.args[0], manip.args[1]);
                        break;
                    default:
                        break;
                }

            }


        }
        // match_elements.forEach(function (e) {
        //     for(i)
        //     e.style.display = "none";
        // });

    },
    hideElement: function (frm, selector, select_from_document = false, closest = true) {
        // document.open();
        // document.write(new_content);
        // document.close();
        let el = frm;
        if (select_from_document)
            el = document.querySelectorAll(selector);
        else if (closest)
            el = [frm.closest(selector)];
        else
            el = frm.querySelectorAll(selector);
        console.log(frm, el);
        el.forEach(function (e) {
            e.style.display = "none";
        });

    },

    updateState: function (el, new_state) {
        ElementaryFlask.updateDict(el, new_state);
    },


    updateDict: function (obj, src) {
        for (const key in src) {
            // console.log('Type of ' + key + ' is: ' + typeof src[key] + '/' + typeof obj[key]);
            // console.log(src[key]);
            if (key in obj && Array.isArray(src[key]) && Array.isArray(obj[key]))
                ElementaryFlask.updateArray(obj[key], src[key]);
            else if (key in obj && typeof src[key] == 'object' && typeof obj[key] == 'object')
                ElementaryFlask.updateDict(obj[key], src[key]);
            else
                obj[key] = src[key];
        }
    },

    updateArray: function (arr1, arr2) {
        arr1.length = 0;
        for (const key in arr2) arr1.push(arr2[key]);

    },

    statefulForm: function (formState) {
        return {
            formId: formState.id,
            formState: formState,
            formElement: null,
            // idSuffix: idSuffix,
            submitForm() {

                // this.formMessage = "";
                // this.formLoading = false;
                // this.buttonText = "Submitting...";
                fetch(this.formState.uri, {
                    method: "POST",
                    body: new FormData(this.getFormElement()),

                    // headers: {
                    //     "Content-Type": "application/json",
                    //     Accept: "application/json",
                    // },
                    // body: JSON.stringify(this.formData),
                })
                    .then(response => response.json())
                    .then(data => {
                        ElementaryFlask.formResponse(data, this.formElement, this);

                    })
                    .catch(() => {
                        console.error('Error:', error);
                        ElementaryFlask.toast(error);
                    })
                    .finally(() => {
                        // this.formLoading = false;
                        // this.buttonText = "Submit";
                    });
            },
            getFormElement() {
                if (this.formElement == null) {
                    this.formElement = document.getElementById(this.formState.id);
                }
                return this.formElement;
            },


        };
    },

    initListingCheckboxes: function (parent = null) {
        let lastChecked = null;
        if (!parent) {
            parent = document;
        }

        const chkboxes = Array.from(parent.querySelectorAll('.fl-checkbox'));
        const links = Array.from(parent.querySelectorAll('.fl-select-link'));
        const batch_buttons = parent.querySelector('.fl-batch-buttons');
        const select_all_button = links[0];
        const select_all_checkbox = select_all_button.querySelector('input');
        // const select_all_checkbox = links[0];


        const is_checked = (el) => el.checked;
        const update_batch_buttons_visibility = (show) => {
            if (batch_buttons) {
                if (show) {
                    batch_buttons.classList.remove("d-none");
                } else {
                    batch_buttons.classList.add("d-none");
                }
            }
        };

        const update_select_all_checkbox = (state) => {
            if (select_all_checkbox) {
                switch (state) {
                    case 'all':
                        select_all_checkbox.checked = true;
                        select_all_checkbox.indeterminate = false;
                        // select_all_checkbox.innerHTML = '☐';
                        break;
                    case 'some':
                        select_all_checkbox.checked = false;
                        select_all_checkbox.indeterminate = true;
                        // select_all_checkbox.innerHTML = '☑';
                        break;
                    default:
                        select_all_checkbox.checked = false;
                        select_all_checkbox.indeterminate = false;
                    // select_all_checkbox.innerHTML = '';

                }
            }
        };


        const update_on_change = () => {
            let checked = chkboxes.filter(is_checked);
            if (checked.length === chkboxes.length && checked.length) { // all
                update_batch_buttons_visibility(true);
                update_select_all_checkbox('all');
            } else if (checked.length > 0) { // some
                update_batch_buttons_visibility(true);
                update_select_all_checkbox('some');
            } else { // none
                update_batch_buttons_visibility(false);
                update_select_all_checkbox('none');
            }

        };

        chkboxes.forEach(item => {
            item.addEventListener('click', event => {
                let currentChecked = event.target;

                if (lastChecked) {
                    if (event.shiftKey) {
                        let start = chkboxes.indexOf(currentChecked);
                        let end = chkboxes.indexOf(lastChecked);


                        chkboxes.slice(Math.min(start, end), Math.max(start, end) + 1).forEach(item => {
                            item.checked = lastChecked.checked;
                        });
                    }
                }

                lastChecked = currentChecked;
                update_on_change();
                event.stopPropagation();
            })
        });

        links.forEach(item => {
            item.addEventListener('click', event => {
                let select_type = event.target.dataset.select;
                lastChecked = null;
                let default_state = !chkboxes.every(is_checked);

                chkboxes.forEach(item => {
                    switch (select_type) {
                        case 'all':
                            item.checked = true;
                            break;
                        case 'none':
                            item.checked = false;
                            break;
                        case 'reverse':
                            item.checked = !item.checked;
                            break;
                        default:
                            item.checked = default_state;

                    }

                });

                update_on_change();
                event.stopPropagation();

            })
        });

        // select_all_checkbox.addEventListener('click', event => {
        //     console.log('test');
        //     select_all_button.click();
        //     event.stopPropagation();
        // })

        update_on_change();

    }
};