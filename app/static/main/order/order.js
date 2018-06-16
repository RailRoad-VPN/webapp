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

    var emailCheckURL = $("meta#email_check_url").data("url");

    var $form = $(".order-form");
    var $packInput = $("#pack_id");
    var $emailInput = $("#email-input");
    var $passwordInput = $("#password-input");
    var $passwordConfirmInput = $("#repeat-password-input");

    var ACCOUNT_CREATED = false;

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
        var need_create_order = false;

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
                // if account was created - just to step
                if (ACCOUNT_CREATED) {
                    is_allow_next_step = true;
                    need_create_order = false;
                } else {
                    is_allow_next_step = accountToPayment();
                    need_create_order = true;
                }
            } else if (currentStepId === 'payment') {
                is_allow_next_step = finish();
            }
        }

        if (!is_allow_next_step) {
            return;
        }

        var $newStep = $('.order-progress-step[data-id="' + newStepId + '"]');
        var $newStepFieldset = $('fieldset[data-id="' + newStepId + '"]');
        var $currentStepFieldset = $('fieldset[data-id="' + currentStepId + '"]');

        if (need_create_order) {
            createOrder(function () {
                _goToStep($currentStepFieldset, $currentStep, $newStep, progress_direction, $newStepFieldset);
            })
        } else {
            _goToStep($currentStepFieldset, $currentStep, $newStep, progress_direction, $newStepFieldset);
        }
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
        var is_ok = checkPassword();
        if (!is_ok) {
            return false;
        }
        return checkRepeatPassword();
    }

    function finish() {
        return true;
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

        var type = 'GET';
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

        doAjax(emailCheckURL, type, data, isAsync, successCallback, errorCallback)
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

    function markInput($input, is_valid) {
        if (is_valid) {
            $input.removeClass('is-invalid').addClass('is-valid');
        } else {
            $input.removeClass('is-valid').addClass('is-invalid');
        }
    }

    function createOrder(callback) {
        $form.ajaxSubmit({
            success: function (response) {
                if (response['success']) {
                    console.log(JSON.stringify(response));
                    // set order code number and email
                    var data = response['data'];
                    $("#order_code").text(data['order']['code']);
                    $("#account_email").text(data['user']['email']);
                    // hide create account fields and show text
                    $("#create_account").remove();
                    $("#created_account").show();
                    ACCOUNT_CREATED = true
                    callback()
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
        })
    }
});
