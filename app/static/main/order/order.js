'use strict';

function bar_progress(direction) {
    var $progressBar = $("#progress-bar");
    var number_of_steps = $progressBar.data('number-of-steps');
    var now_value = $progressBar.data('now-value');
    var new_value = 0;
    if (direction === 'right') {
        new_value = now_value + ( 100 / number_of_steps );
    } else if (direction === 'left') {
        new_value = now_value - ( 100 / number_of_steps );
    }
    $progressBar.attr('style', 'width: ' + new_value + '%;').data('now-value', new_value);
}


// account details save in local storage
var LS_ORDER_KEY = 'order';
var LS_ORDER_PACK_ID_KEY = 'pack_id';
var LS_ORDER_ACCOUNT_KEY = 'account';
var LS_ORDER_ACCOUNT_EMAIL_KEY = 'email';
var LS_ORDER_ACCOUNT_PASSWORD_KEY = 'password';
var LS_ORDER_ACCOUNT_PASSWORD_CONFIRM_KEY = 'password_confirm';

$(document).ready(function () {
    var $emailCheckURLObj = $("meta#email_check_url");
    var $orderPageURLObj = $("meta#order_page_url");
    var $getPaymentUrlURLObj = $("meta#get_payment_url_url");

    var $orderForm = $('.order-form');
    var $userUuidInput = $("#user_uuid");
    var $packInput = $("#pack_id");
    var $emailInput = $("#email-input");
    var $passwordInput = $("#password-input");
    var $passwordConfirmInput = $("#repeat-password-input");

    var $paymentMethodsModal = $("#payment_methods-modal");

    var USER_REGISTERED = !!$userUuidInput.val();

    var ORDER_LS = getFromLocalStorage(LS_ORDER_KEY);
    var ACCOUNT_LS;
    if (ORDER_LS) {
        ACCOUNT_LS = ORDER_LS[LS_ORDER_ACCOUNT_KEY];
    } else {
        ORDER_LS = {}
    }

    if (!ACCOUNT_LS) {
        ACCOUNT_LS = {}
    }

    function restoreOrderFromLS() {
        if (ORDER_LS) {
            $packInput.val(ORDER_LS[LS_ORDER_PACK_ID_KEY]);
            if (ACCOUNT_LS) {
                $emailInput.val(ACCOUNT_LS[LS_ORDER_ACCOUNT_EMAIL_KEY]);
                checkEmail();
                $passwordInput.val(ACCOUNT_LS[LS_ORDER_ACCOUNT_PASSWORD_KEY]);
                checkPassword();
                $passwordConfirmInput.val(ACCOUNT_LS[LS_ORDER_ACCOUNT_PASSWORD_CONFIRM_KEY]);
                checkRepeatPassword();
            }
        }
    }

    function checkPackChosen() {
        if (window.location.href.indexOf('pack=') !== -1 || (ORDER_LS && ORDER_LS[LS_ORDER_PACK_ID_KEY])) {
            if (window.location.href.indexOf('pack=') !== -1) {
                ORDER_LS[LS_ORDER_PACK_ID_KEY] = getUrlParameter('pack');
                setToLocalStorage(LS_ORDER_KEY, ORDER_LS);
            } else {
                window.location = $orderPageURLObj.data('url') + "?pack=" + ORDER_LS[LS_ORDER_PACK_ID_KEY]
            }
            goToStep('right', 'account');
        } else {
            $('#pack-fieldset').fadeIn('slow');
        }
    }

    restoreOrderFromLS();

    checkPackChosen();

    // checkout sub btn
    $('.btn-checkout').on('click', function () {
        ORDER_LS[LS_ORDER_PACK_ID_KEY] = $(this).data('id');
        var is_ok = setToLocalStorage(LS_ORDER_KEY, ORDER_LS);
        // for case when used local storage but browser does not support it
        if (!is_ok) {
            $packInput.val($(this).data('id'));
        }
    });

    // next step
    $('.order-form .btn-next').on('click', function () {
        goToStep('right');
    });

    // previous step
    $('.order-form .btn-previous').on('click', function () {
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
        var $currentStep = $('.order-form').find('.order-progress-step.active');
        var currentStepId = $currentStep.data('id');

        var is_allow_next_step = true;

        if (!newStepId || newStepId === '') {
            if (progress_direction === 'left') {
                newStepId = $currentStep.prev().data('id');
            } else {
                newStepId = $currentStep.next().data('id');
            }
        }

        if (progress_direction === 'right') {
            is_allow_next_step = stepFieldSetValidation(currentStepId);

            // business logic
            if (currentStepId === 'pack') {
                is_allow_next_step = packToAccount();
            } else if (currentStepId === 'account') {
                is_allow_next_step = accountToPayment();
            }
        }

        if (!is_allow_next_step) {
            return;
        }

        var $newStep = $('.order-progress-step[data-id="' + newStepId + '"]');
        var $newStepFieldset = $('fieldset[data-id="' + newStepId + '"]');
        var $currentStepFieldset = $('fieldset[data-id="' + currentStepId + '"]');

        _goToStep($currentStepFieldset, $currentStep, $newStep, progress_direction, $newStepFieldset);
    }

    function _goToStep($currentStepFieldset, $currentStep, $newStep, progress_direction, $newStepFieldset) {
        if (progress_direction === 'right') {
            $currentStep.addClass('activated');
        }
        $currentStep.addClass('activated');
        // hide new step fieldset
        $currentStepFieldset.fadeOut(400, function () {
            $currentStep.removeClass('active');
            $newStep.addClass('active').removeClass('activated');
            // progress bar
            bar_progress(progress_direction);
            // show new step fieldset
            $newStepFieldset.fadeIn();
            // scroll window to beginning of the form
            scrollToTop();
        });
    }

    function packToAccount(subscriptionIdVal) {
        if (!subscriptionIdVal) {
            subscriptionIdVal = getUrlParameter('pack');
            if (!subscriptionIdVal) {
                subscriptionIdVal = ORDER_LS[LS_ORDER_PACK_ID_KEY];
                if (!subscriptionIdVal) {
                    // for case when used local storage but browser does not support it
                    subscriptionIdVal = $packInput.val();
                    if (!subscriptionIdVal) {
                        return false
                    }
                }
            }
        }
        $packInput.val(subscriptionIdVal);
        return true;
    }

    function accountToPayment() {
        if (USER_REGISTERED) {
            return true;
        }
        var is_pwd_ok = checkPassword();
        if (!is_pwd_ok) {
            return false;
        }
        is_pwd_ok = checkRepeatPassword();
        return is_pwd_ok;
    }

    function stepFieldSetValidation(currentStepId) {
        var is_alllow = true;
        $('fieldset[data-id="' + currentStepId + '"]').find('input[type="text"], input[type="password"]').each(function () {
            if ($.trim($(this).val()) === "") {
                markInput($(this), false);
                $(this).parent().find('.empty_error').show();
                is_alllow = false;
            } else {
                markInput($(this), true);
                $(this).parent().find('.empty_error').hide();
            }
        });
        return is_alllow
    }

    // prevent form submit by pressing enter button
    $(window).keydown(function (event) {
        if (event.keyCode === 13) {
            event.preventDefault();
            return false;
        }
    });

    $orderForm.on('submit', function (e) {
        e.preventDefault();
        var paymentMethodVal = $.trim($("#payment_method").val());
        if (!paymentMethodVal || paymentMethodVal === '') {
            $('#payment-method-error').show();
            return false;
        }
        var that = this;
        $(that).ajaxSubmit({
            success: function (response) {
                if (response['success']) {
                    console.log(JSON.stringify(response));
                    getPaymentPageURL(function () {
                        setToLocalStorage(LS_ORDER_KEY, '');
                    });
                } else {
                    if (response.hasOwnProperty('errors')) {
                        showErrors(response);
                    }
                }
            },
            error: function (response) {
                console.log(JSON.stringify(response));
                notyError("error");
            }
        });
    });

    function getPaymentPageURL(callback) {
        var orderCodeVal = $.trim($("#order_code").text());
        var subscriptionIdVal = $.trim($("#subscription-id").val());
        var paymentMethodVal = $.trim($("#payment_method").val());

        var getPaymentURL = $getPaymentUrlURLObj.data('url');
        var getPaymentURLMethod = $getPaymentUrlURLObj.data('method');

        redirectToPaymentPage(orderCodeVal, subscriptionIdVal, paymentMethodVal, 'order', getPaymentURL,
            getPaymentURLMethod, callback);
    }

    $paymentMethodsModal.on('hide.bs.modal', function (e) {
        // if in modal nothing was chosen - do nothing
        if ($paymentMethodsModal.find('.modal-body').find('.payment-method.active').length === 0) {
            return;
        }
        var $activePaymentMethodClone = $(".payment-method.active").parent().clone();
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

    $emailInput.on('focusout', function () {
        checkEmail();
    });

    $passwordInput.on('focusout', function () {
        checkPassword();
        checkRepeatPassword();
    });

    $passwordConfirmInput.on('focusout', function () {
        checkRepeatPassword();
    });

    function checkEmail() {
        var emailVal = $.trim($emailInput.val());
        if (emailVal === '') {
            markInput($emailInput, false);
            $emailInput.parent().find('.empty_error').show();
            return false;
        }

        var data = {
            'email': emailVal,
        };
        var isAsync = true;

        var successCallback = function (response) {
            if (response.hasOwnProperty('success') && !response['success']) {
                $emailInput.parent().find('.busy_error').show();
                markInput($emailInput, false);
            } else {
                $emailInput.parent().find('.busy_error').hide();
                markInput($emailInput, true);
                // update local storage
                ACCOUNT_LS[LS_ORDER_ACCOUNT_EMAIL_KEY] = emailVal;
                ORDER_LS[LS_ORDER_ACCOUNT_KEY] = ACCOUNT_LS;
                setToLocalStorage(LS_ORDER_KEY, ORDER_LS);
            }
        };

        var errorCallback = function (response) {
            notyError("System Error");
        };

        doAjax($emailCheckURLObj.data('url'), $emailCheckURLObj.data('method'), data, isAsync, successCallback, errorCallback)
    }

    function checkPassword() {
        var pwdVal = $.trim($passwordInput.val());
        var $pwdFormGroup = $passwordInput.parent();

        if (pwdVal === '') {
            $pwdFormGroup.find('.empty_error').show();
            markInput($passwordInput, false);
            return false;
        } else if (pwdVal.length < 6) {
            $pwdFormGroup.find('.short_error').show();
            markInput($passwordInput, false);
            return false;
        } else {
            $pwdFormGroup.find('.short_error').hide();
            markInput($passwordInput, true);

            ACCOUNT_LS[LS_ORDER_ACCOUNT_PASSWORD_KEY] = pwdVal;
            ORDER_LS[LS_ORDER_ACCOUNT_KEY] = ACCOUNT_LS;
            setToLocalStorage(LS_ORDER_KEY, ORDER_LS);
            return true;
        }
    }

    function checkRepeatPassword() {
        var pwdVal = $.trim($passwordInput.val());
        var pwdConfirmVal = $.trim($passwordConfirmInput.val());

        if (pwdConfirmVal === '') {
            markInput($passwordConfirmInput, false);
            $passwordConfirmInput.parent().find('.empty_error').show();
            return false;
        }

        if (pwdVal !== pwdConfirmVal) {
            markInput($passwordConfirmInput, false);
            $passwordConfirmInput.parent().find('.match_error').show();
            return false;
        } else {
            markInput($passwordConfirmInput, true);
            $passwordConfirmInput.parent().find('.match_error').hide();

            ACCOUNT_LS[LS_ORDER_ACCOUNT_PASSWORD_CONFIRM_KEY] = pwdConfirmVal;
            ORDER_LS[LS_ORDER_ACCOUNT_KEY] = ACCOUNT_LS;
            setToLocalStorage(LS_ORDER_KEY, ORDER_LS);
            return true;
        }
    }
});
