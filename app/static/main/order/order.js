'use strict';

// account details save in local storage
const
    LS_ORDER_KEY = 'order',
    LS_ORDER_PACK_ID_KEY = 'pack_id',
    LS_ORDER_ACCOUNT_KEY = 'account',
    LS_ORDER_ACCOUNT_EMAIL_KEY = 'email',
    LS_ORDER_ACCOUNT_PASSWORD_KEY = 'password',
    LS_ORDER_ACCOUNT_PASSWORD_CONFIRM_KEY = 'password_confirm';

$(window).on('load', function () {
    const $profilePageURLObj = $("meta#profile_page_url");
    const $emailCheckURLObj = $("meta#email_check_url");
    const $isTrialAvailableURLObj = $("meta#is_trial_available_url");
    const $chosenSubTemplateURLObj = $("meta#chosen_sub_url");
    const $chooseServicePackURLObj = $("meta#choose_service_pack_url");

    const $subscriptionDataObj = $("#subscriptionsData");

    const $orderForm = $('.order-form');
    const $userUuidInput = $("#user_uuid");
    const $packInput = $("#pack_id");
    const $emailInput = $("#email-input");
    const $passwordInput = $("#password-input");
    const $passwordConfirmInput = $("#repeat-password-input");

    const $paymentMethodsModal = $("#payment_methods-modal");

    let VPN_FREE, VPN_TRIAL, UNDERSCORE_CHOSEN_SUB_TMPLT, USER_REGISTERED, ORDER_LS, CHOSEN_PACK, ACCOUNT_LS;

    blockPage(null, init);

    $(".order-progress-step").on('click', function () {
        const stepId = $(this).data('id');

        goToStep(null, stepId);
    });

    // checkout sub btn
    $('.btn-checkout').on('click', function () {
        CHOSEN_PACK = $(this).data('id');
        setChosenPack(CHOSEN_PACK, function () {
            goToStep('right');
        });
    });

    // next step
    $(document).on('click', ".order-form .btn-next", function () {
        goToStep('right');
    });

    // previous step
    $(document).on('click', ".order-form .btn-previous", function () {
        goToStep('left');
    });

    // input focus
    $('.order-form input[type="text"], .order-form input[type="password"], .order-form textarea').on('focus', function () {
        markInput($(this), true);
    });

    $('input[type="text"], input[type="password"]').on('focus', function () {
        $(this).parent().find('.error').hide();
    });

    function goToStep(progress_direction, newStepId) {
        let $currentStep = $('.order-form').find('.order-progress-step.active');
        let currentStepId = $currentStep.data('id');

        if (!newStepId || newStepId === '') {
            if (progress_direction === 'left') {
                newStepId = $currentStep.prev().data('id');
            } else {
                newStepId = $currentStep.next().data('id');
            }
        }

        let $newStep = $('.order-progress-step[data-id="' + newStepId + '"]');
        let $newStepFieldset = $('fieldset[data-id="' + newStepId + '"]');
        let $currentStepFieldset = $('fieldset[data-id="' + currentStepId + '"]');

        const
            newStepNum = $newStep.data("num"),
            currStepNum = $currentStep.data("num");

        let byStep = false;
        // business logic for newStep move
        if (!progress_direction) {
            byStep = true;
            if (parseInt(newStepNum) > parseInt(currStepNum)) {
                progress_direction = 'right';
            }
        }

        // business logic for right direction
        if (progress_direction === 'right') {
            if (currentStepId === 'pack') {
                packToAccount(function () {
                    _goToStep($currentStepFieldset, $currentStep, $newStep, progress_direction, $newStepFieldset, currStepNum, newStepNum, byStep);
                });
            } else if (currentStepId === 'account') {
                accountToPayment(function () {
                    _goToStep($currentStepFieldset, $currentStep, $newStep, progress_direction, $newStepFieldset, currStepNum, newStepNum, byStep);
                });
            }
        } else {
            _goToStep($currentStepFieldset, $currentStep, $newStep, progress_direction, $newStepFieldset, currStepNum, newStepNum, byStep);
        }
    }

    function _goToStep($currentStepFieldset, $currentStep, $newStep, progress_direction, $newStepFieldset, currStepNum, newStepNum, byStep) {
        if (progress_direction === 'right') {
            $currentStep.addClass('activated');
        } else {
            $currentStep.removeClass('activated')
        }

        if (byStep) {
            for (let i = 0; i <= newStepNum; i++) {
                $('.order-progress-step[data-num="' + i + '"]').addClass('activated');
            }

            if (newStepNum < currStepNum) {
                for (let i = newStepNum; i <= currStepNum; i++) {
                    $('.order-progress-step[data-num="' + i + '"]').removeClass('activated');
                }
            }
        }

        // progress bar
        stepProgressBar(currStepNum, newStepNum);

        // hide new step fieldset
        $currentStepFieldset.fadeOut(400, function () {
            $currentStep.removeClass('active');
            $newStep.addClass('active').removeClass('activated');
            // show new step fieldset
            $newStepFieldset.fadeIn();
            // scroll window to beginning of the form
            scrollToTop();
        });
    }

    function stepProgressBar(currStepNum, newStepNum) {
        const $progressBar = $("#progress-bar");
        const number_of_steps = $progressBar.data('number-of-steps');
        const step = 100 / number_of_steps;

        let new_value = newStepNum * step;

        $progressBar.attr('style', 'width: ' + new_value + '%;').data('now-value', new_value);
    }

    function packToAccount(successCb) {
        let analytics_evt_data = get_analytices_data();
        analytics_evt_data['action'] = 'pack_to_account';

        const subsJSON = $subscriptionDataObj.data('dict');
        const chosenSubJSON = subsJSON[CHOSEN_PACK];
        analytics_evt_data['pack_id'] = CHOSEN_PACK;

        if (!chosenSubJSON) {
            analytics_evt_data['description'] = "deny move, pack was no chosen";
            analytics_event('order', analytics_evt_data);
            goToStep(null, 'pack');
            return false;
        }
        try {
            $(".chosen-subscription-name").text(chosenSubJSON['service_name']);
        } catch (TypeError) {
            goToStep(null, 'pack');
            analytics_evt_data['description'] = "type error when try to get service name from subscription json";
            analytics_event('order', analytics_evt_data);
            return false;
        }
        chosenSubJSON['features'] = [];
        let $featuresHtml = $(".subscription-" + chosenSubJSON['id']).filter(function () {
            return $(this).css('display') === 'block';
        });
        $featuresHtml.find("ul.pricing-content span").each(function () {
            const feature = {
                "name": $(this).text(),
                "enabled": !$(this).parent().hasClass("no-feature")
            };
            let chosensubFeatures = chosenSubJSON['features'];
            chosensubFeatures.push(feature);
        });
        let subJSON = {"chosen_subscription": chosenSubJSON, "width": "width: 18rem;"};
        let html = UNDERSCORE_CHOSEN_SUB_TMPLT(subJSON);
        $(".chosen-subscription").html(html);
        subJSON = {"chosen_subscription": subsJSON[CHOSEN_PACK], "width": ""};
        html = UNDERSCORE_CHOSEN_SUB_TMPLT(subJSON);
        $(".chosen-subscription-mini").html(html);

        analytics_evt_data['description'] = "access move";
        analytics_event('order', analytics_evt_data);

        checkTrialAvailable(successCb);
    }

    function accountToPayment(successCb) {
        let analytics_evt_data = get_analytices_data();
        analytics_evt_data['action'] = 'account_to_payment';

        const subsJSON = $subscriptionDataObj.data('dict');
        const chosenSubJSON = subsJSON[CHOSEN_PACK];

        analytics_evt_data['pack_id'] = CHOSEN_PACK;

        // TODO promo or some sale price will be here
        $(".last_step-price").text("$" + chosenSubJSON['price']);

        if (!USER_REGISTERED) {
            let is_pwd_ok = checkPassword();
            if (!is_pwd_ok) {
                analytics_evt_data['description'] = "deny move, password not ok";
                analytics_event('order', analytics_evt_data);
                return false;
            }
            is_pwd_ok = checkRepeatPassword();
            if (!is_pwd_ok) {
                analytics_evt_data['description'] = "deny move, password repeat not ok";
                analytics_event('order', analytics_evt_data);
                return false;
            }

            if ($emailInput.hasClass('is-invalid')) {
                analytics_evt_data['description'] = "deny move, email not ok";
                analytics_event('order', analytics_evt_data);
                return false;
            }
        }

        analytics_evt_data['description'] = "access move";
        analytics_event('order', analytics_evt_data);

        checkTrialAvailable(function () {
            if (!USER_REGISTERED) {
                checkEmail(successCb);
            } else {
                successCb();
            }

            // free subscription
            if (parseInt(chosenSubJSON['price']) === 0) {
                VPN_FREE = true;
                $(".need_payment").hide();
                $(".free_payment").show();
                $(".trial_payment").hide()
                // trial subscription
            } else if (chosenSubJSON['is_trial'] && VPN_TRIAL) {
                $(".need_payment").hide();
                $(".free_payment").hide();
                $(".trial_payment").show();
                $(".trial_days").text(chosenSubJSON['trial_period_days']);
                $(".last_step-price").text("$0.00");
            } else {
                $(".need_payment").show();
                $(".free_payment").hide();
                $(".trial_payment").hide()
            }
        });
    }

    // prevent form submit by pressing enter button
    $(window).keydown(function (event) {
        if (event.keyCode === 13) {
            event.preventDefault();
            return false;
        }
    });

    $orderForm.on('submit', function (e) {
        let analytics_evt_data = get_analytices_data();
        analytics_evt_data['action'] = 'submit';
        e.preventDefault();
        if (VPN_FREE !== true && VPN_TRIAL !== true) {
            let paymentMethodVal = $.trim($("#payment_method").val());
            if (!paymentMethodVal || paymentMethodVal === '') {
                $('#payment-method-error').show();
                analytics_evt_data['description'] = 'vpn free and trial not available and payment method not chosen. show payments';
                analytics_event('order', analytics_evt_data);
                return false;
            }
        }

        let that = this;

        blockPage(null, function () {
            $(that).ajaxSubmit({
                success: function (response) {
                    if (response['success']) {
                        analytics_evt_data['success'] = 'true';
                        analytics_event('order', analytics_evt_data);
                        window.location = $profilePageURLObj.data("url");
                    } else {
                        analytics_evt_data['success'] = 'false';
                        analytics_event('order', analytics_evt_data);
                        if (response.hasOwnProperty('errors')) {
                            showErrors(response);
                        }
                        unblockPage()
                    }
                    unblockPage();
                },
                error: function (response) {
                    console.log(JSON.stringify(response));
                    notyError("error");
                    unblockPage();
                }
            });
        });
    });

    $paymentMethodsModal.on('hide.bs.modal', function (e) {
        // if in modal nothing was chosen - do nothing
        if ($paymentMethodsModal.find('.modal-body').find('.payment-method.active').length === 0) {
            return;
        }
        let $activePaymentMethodClone = $(".payment-method.active").parent().clone();
        // css fix
        $activePaymentMethodClone.addClass('col-xl-2');
        $("#payment_methods-container").append($activePaymentMethodClone);
    });

    $(document).on('click', ".payment-method", function () {
        $('#payment-method-error').hide();
        if ($(this).hasClass('active')) {
            return;
        }

        $(".payment-method.active").removeClass('active');
        $(this).addClass('active');

        // delete payment method from main container only if modal with additional methods was shown
        if ($paymentMethodsModal.hasClass('show')) {
            $("#payment_methods-container").find('.payment-method.additional').parent().remove();
            $paymentMethodsModal.modal('hide');
        }
        $("#payment_method").val($(this).data('id'));
    });

    $emailInput.on('focusout keyup keypress blur change', function () {
        checkEmail();
    });

    $passwordInput.on('focusout keyup keypress blur change', function () {
        checkPassword();
        checkRepeatPassword();
    });

    $passwordConfirmInput.on('focusout keyup keypress blur change', function () {
        checkRepeatPassword();
    });

    function checkTrialAvailable(successCb) {
        const isAsync = true;

        const successCallback = function (response) {
            if (response.hasOwnProperty('success') && response['success']) {
                VPN_TRIAL = response['data']['is_vpn_trial'];
            } else {
                VPN_TRIAL = false;
            }

            if (successCb) successCb();
        };

        const errorCallback = function (response) {
            notyError("System Error");
        };

        doAjax($isTrialAvailableURLObj.data('url'), $isTrialAvailableURLObj.data('method'), {},
            isAsync, successCallback, errorCallback);
    }

    function checkEmail(successCb) {
        let isEmailEmpty;
        let emailVal = $.trim($emailInput.val());
        if (emailVal === '') {
            markInput($emailInput, false);
            $emailInput.parent().find('.empty_error').show();
            isEmailEmpty = true;
            return false;
        } else if (emailVal.indexOf("@") === -1) {
            markInput($emailInput, false);
            $emailInput.parent().find('.empty_error').show();
            isEmailEmpty = true;
            return false;
        } else {
            isEmailEmpty = false;
        }

        let data = {
            'email': emailVal,
        };

        const isAsync = true;

        const successCallback = function (response) {
            if (response.hasOwnProperty('success') && !response['success']) {
                $emailInput.parent().find('.busy_error').show();
                markInput($emailInput, false);
            } else {
                $emailInput.parent().find('.busy_error').hide();
                // update local storage
                ACCOUNT_LS[LS_ORDER_ACCOUNT_EMAIL_KEY] = emailVal;
                ORDER_LS[LS_ORDER_ACCOUNT_KEY] = ACCOUNT_LS;
                setToLocalStorage(LS_ORDER_KEY, ORDER_LS);

                if (isEmailEmpty === false) {
                    $emailInput.parent().find('.empty_error').hide();
                    markInput($emailInput, true);
                    if (successCb) successCb();
                }
            }
        };

        const errorCallback = function (response) {
            notyError("System Error");
        };

        doAjax($emailCheckURLObj.data('url'), $emailCheckURLObj.data('method'), data, isAsync, successCallback, errorCallback);
    }

    function checkPassword() {
        const pwdVal = $.trim($passwordInput.val());
        const $pwdFormGroup = $passwordInput.parent();

        if (pwdVal === '') {
            $pwdFormGroup.find('.empty_error').show();
            markInput($passwordInput, false);
            return false;
        } else if (pwdVal.length < 6) {
            $pwdFormGroup.find('.empty_error').hide();
            $pwdFormGroup.find('.short_error').show();
            markInput($passwordInput, false);
            return false;
        } else {
            $pwdFormGroup.find('.empty_error').hide();
            $pwdFormGroup.find('.short_error').hide();
            markInput($passwordInput, true);

            ACCOUNT_LS[LS_ORDER_ACCOUNT_PASSWORD_KEY] = pwdVal;
            ORDER_LS[LS_ORDER_ACCOUNT_KEY] = ACCOUNT_LS;
            setToLocalStorage(LS_ORDER_KEY, ORDER_LS);
            return true;
        }
    }

    function checkRepeatPassword() {
        const pwdVal = $.trim($passwordInput.val());
        const pwdConfirmVal = $.trim($passwordConfirmInput.val());

        if (pwdConfirmVal === '') {
            markInput($passwordConfirmInput, false);
            $passwordConfirmInput.parent().find('.empty_error').show();
            return false;
        }

        if (pwdVal !== pwdConfirmVal) {
            $passwordConfirmInput.parent().find('.empty_error').hide();
            markInput($passwordConfirmInput, false);
            $passwordConfirmInput.parent().find('.match_error').show();
            return false;
        } else {
            markInput($passwordConfirmInput, true);
            $passwordConfirmInput.parent().find('.empty_error').hide();
            $passwordConfirmInput.parent().find('.match_error').hide();

            ACCOUNT_LS[LS_ORDER_ACCOUNT_PASSWORD_CONFIRM_KEY] = pwdConfirmVal;
            ORDER_LS[LS_ORDER_ACCOUNT_KEY] = ACCOUNT_LS;
            setToLocalStorage(LS_ORDER_KEY, ORDER_LS);
            return true;
        }
    }

    function init() {
        // format
        const subsJSON = $subscriptionDataObj.data('json');
        let subsObj = {};
        for (let i = 0; i < subsJSON.length; i++) {
            const sub = subsJSON[i];
            const subId = sub['id'];
            subsObj[subId] = sub;
        }

        $subscriptionDataObj.data('dict', subsObj);

        USER_REGISTERED = !!$userUuidInput.val();
        ORDER_LS = getFromLocalStorage(LS_ORDER_KEY);
        CHOSEN_PACK = -1;

        restorePageState();
        loadUnderscoreTemplates(function () {
            if (!CHOSEN_PACK || CHOSEN_PACK === -1) {
                $('#pack-fieldset').fadeIn('slow');
            } else {
                $packInput.val(CHOSEN_PACK);
                setChosenPack(CHOSEN_PACK, function () {
                    goToStep('right');
                });
            }
            unblockPage();
        });
    }

    function loadUnderscoreTemplates(cb) {
        $.ajax({
            url: $chosenSubTemplateURLObj.data("url"),
            method: $chosenSubTemplateURLObj.data("method"),
            async: false,
            dataType: 'html',
            success: function (data) {
                UNDERSCORE_CHOSEN_SUB_TMPLT = _.template(data);
                if (cb) cb();
            },
            error: function (data) {
                console.log(data);
            }
        });
    }

    function restorePageState() {
        if (ORDER_LS) {
            ACCOUNT_LS = ORDER_LS[LS_ORDER_ACCOUNT_KEY];
        } else {
            ORDER_LS = {};
        }

        if (!ACCOUNT_LS) {
            ACCOUNT_LS = {};
        }

        if (!USER_REGISTERED) {
            // restore state from localstorage
            if (ORDER_LS) {
                CHOSEN_PACK = ORDER_LS[LS_ORDER_PACK_ID_KEY];
                if (ACCOUNT_LS) {
                    if (ACCOUNT_LS.hasOwnProperty(LS_ORDER_ACCOUNT_EMAIL_KEY)) {
                        $emailInput.val(ACCOUNT_LS[LS_ORDER_ACCOUNT_EMAIL_KEY]);
                        checkEmail();
                    }
                    if (ACCOUNT_LS.hasOwnProperty(LS_ORDER_ACCOUNT_PASSWORD_KEY)) {
                        $passwordInput.val(ACCOUNT_LS[LS_ORDER_ACCOUNT_PASSWORD_KEY]);
                        checkPassword();
                    }
                    if (ACCOUNT_LS.hasOwnProperty(LS_ORDER_ACCOUNT_PASSWORD_CONFIRM_KEY)) {
                        $passwordConfirmInput.val(ACCOUNT_LS[LS_ORDER_ACCOUNT_PASSWORD_CONFIRM_KEY]);
                        checkRepeatPassword();
                    }
                }
            }
        }

        CHOSEN_PACK = getChosenPack();
    }

    function getChosenPack() {
        let chosenPack;
        // check in URL query string
        if (window.location.href.indexOf('pack=') !== -1) {
            chosenPack = getUrlParameter('pack');
            if (isLocalStorageSupported()) {
                ORDER_LS[LS_ORDER_PACK_ID_KEY] = chosenPack;
                setToLocalStorage(LS_ORDER_KEY, ORDER_LS);
            }
            $packInput.val(chosenPack);
            return chosenPack;
        }
        if (isLocalStorageSupported()) {
            chosenPack = ORDER_LS[LS_ORDER_PACK_ID_KEY];
        }

        if (!chosenPack) {
            chosenPack = $packInput.val();
        }

        return chosenPack;
    }

    function setChosenPack(chosenPack, successCb) {
        let data = {
            'service_id': chosenPack
        };

        const isAsync = true;

        const successCallback = function (response) {
            if (!response.hasOwnProperty('success') || !response['success']) {
                showErrors(response);
            } else {
                if (isLocalStorageSupported()) {
                    ORDER_LS[LS_ORDER_PACK_ID_KEY] = chosenPack;
                    setToLocalStorage(LS_ORDER_KEY, ORDER_LS);
                }

                if (!chosenPack) {
                    chosenPack = $packInput.val();
                }
                successCb();
            }
        };

        const errorCallback = function (response) {
            notyError("System Error");
        };

        doAjax($chooseServicePackURLObj.data('url'), $chooseServicePackURLObj.data('method'), JSON.stringify(data), isAsync, successCallback, errorCallback);
    }
});