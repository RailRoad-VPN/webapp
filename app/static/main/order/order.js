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

$(document).ready(function () {

    var $emailCheckURLObj = $("meta#email_check_url");
    var $getPaymentUrlURLObj = $("meta#get_payment_url_url");

    var $orderForm = $('.order-form');
    var $packInput = $("#pack_id");
    var $emailInput = $("#email-input");
    var $passwordInput = $("#password-input");
    var $passwordConfirmInput = $("#repeat-password-input");

    var $paymentMethodsModal = $("#payment_methods-modal");

    $(".form-group .error").hide();

    // check chosen pack
    if (window.location.href.indexOf('pack=') !== -1) {
        $("fieldset:first").fadeOut('fast');
        goToStep('right', 'account');
    } else {
        $('.order-form fieldset:first').fadeIn('slow');
    }

    // next step
    $('.btn-next, .btn-checkout').on('click', function () {
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
                is_allow_next_step = packToAccount(this);
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

    function packToAccount(checkoutBtn) {
        var subs_id = $(checkoutBtn).data('subscription_id');
        $packInput.val(subs_id);
        return true;
    }

    function accountToPayment() {
        return true;
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
                    getPaymentPageURL();
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

        var data = {
            'order_code': orderCodeVal,
            'subscription_id': subscriptionIdVal,
            'payment_method_id': paymentMethodVal,
        };
        var isAsync = true;

        var successCallback = function (response) {
            if (response.hasOwnProperty('success') && response['success']) {
                if (response.hasOwnProperty('data')) {
                    window.location = response['data']['redirect_url'];
                } else {
                    callback ? callback() : ''
                }
            } else {
                showErrors(response);
            }
        };

        var errorCallback = function (response) {
            notyError("System Error");
        };

        doAjax($getPaymentUrlURLObj.data('url'), $getPaymentUrlURLObj.data('method'), data, isAsync, successCallback, errorCallback)
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
            }
        };

        var errorCallback = function (response) {
            notyError("System Error");
        };

        doAjax($emailCheckURLObj.data('url'), $emailCheckURLObj.data('method'), data, isAsync, successCallback, errorCallback)
    }

    function checkPassword() {
        var pwd = $.trim($passwordInput.val());
        var $pwdFormGroup = $passwordInput.parent();

        if (pwd === '') {
            $pwdFormGroup.find('.empty_error').show();
            markInput($passwordInput, false);
            return false;
        } else if (pwd.length < 6) {
            $pwdFormGroup.find('.short_error').show();
            markInput($passwordInput, false);
            return false;
        } else {
            $pwdFormGroup.find('.short_error').hide();
            markInput($passwordInput, true);
            return true;
        }
    }

    function checkRepeatPassword() {
        var pwd = $.trim($passwordInput.val());
        var pwdConfirm = $.trim($passwordConfirmInput.val());

        if (pwdConfirm === '') {
            markInput($passwordConfirmInput, false);
            $passwordConfirmInput.parent().find('.empty_error').show();
            return false;
        }

        if (pwd !== pwdConfirm) {
            markInput($passwordConfirmInput, false);
            $passwordConfirmInput.parent().find('.match_error').show();
            return false;
        } else {
            markInput($passwordConfirmInput, true);
            $passwordConfirmInput.parent().find('.match_error').hide();
            return true;
        }
    }
});
