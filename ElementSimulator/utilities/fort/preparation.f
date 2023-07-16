! ==================================================================================================================== !
module Preparation
   implicit none

   integer, parameter :: dp = selected_real_kind(15)
   integer, parameter :: num_fixed_params = 16
   integer, parameter :: num_fixed_states = 20

   private
   
   public Get_Material, Adjust_Default_Materialparameters, Prepare_State, Postprocess_State


   contains


   ! --------------------------------------------------------------- !
   subroutine Get_Material(material_description, igran_active, constitutive_model_name, &
         adj_name, nu, materialparameters, success)
   ! --------------------------------------------------------------- !
      character(len=40), intent(in) :: material_description
      logical, intent(in) :: igran_active
      character(len=9), intent(in) :: constitutive_model_name
      character(len=9), intent(out) :: adj_name
      real(dp), intent(in) :: nu
      real(dp), dimension(num_fixed_params), intent(out) :: materialparameters
      logical, intent(out) :: success
      ! ------------------------------------------------------------ !
      logical :: is_assigned

      is_assigned = .False.
      success = .False.
      materialparameters = 0.0_dp

      if (Uppercase(constitutive_model_name) == 'HYPO-VW96') then
         ! 01     02   03  04    05    06    07     08    09   10   11     12      13
         ! phi_c, h_s, n,  e_d0, e_c0, e_i0, alpha, beta, m_T, m_R, R_max, beta_r, chi
         !
         if (material_description == 'Hamburger Sand 01') then
            materialparameters(1:13) = [ &
               0.55851_dp, 2.0e6_dp, 0.3_dp, 0.5_dp, 0.8_dp, 0.95_dp, 0.1_dp, 1.0_dp, &
               2.0_dp, 5.0_dp, 0.0001_dp, 0.5_dp, 6.0_dp]
            is_assigned = .True.
         else if (material_description == 'Hamburger Sand 02') then
            materialparameters(1:13) = [ &
               0.576_dp, 1.0e6_dp, 0.25_dp, 0.55_dp, 0.95_dp, 1.05_dp, 0.25_dp, 1.5_dp, &
               2.0_dp, 5.0_dp, 0.0001_dp, 0.5_dp, 6.0_dp]
            is_assigned = .True.
         else if (material_description == 'Hamburger Sand 03') then
            materialparameters(1:13) = [ &
               0.5411_dp, 5.8e6_dp, 0.28_dp, 0.53_dp, 0.84_dp, 1.0_dp, 0.13_dp, 1.05_dp, &
               2.0_dp, 5.0_dp, 1.0e-4_dp, 0.5_dp, 2.0_dp]
            is_assigned = .True.
         end if
      !
      else if (Uppercase(constitutive_model_name) == 'HYPO-WU92') then
         if (material_description == 'Wu92 Sand 01') then
            materialparameters(1:4) = [-106.5_dp, -801.5_dp, -797.1_dp, 1077.7_dp]
            is_assigned = .True.
         else if (material_description == 'Wu92 Sand 02') then
            materialparameters(1:4) = [-33.3_dp, -308.4_dp, -306.8_dp, 321.3_dp]
            is_assigned = .True.
         else if (material_description == 'Wu94 Sand 05') then
            materialparameters(1:4) = [-101.2_dp, -962.1_dp, -877.3_dp, 1229.2_dp]
            is_assigned = .True.
         else if (material_description == 'Wu94 Sand 06') then
            materialparameters(1:4) = [-69.4_dp, -673.1_dp, -655.9_dp, 699.6_dp]
            is_assigned = .True.
         end if
      !
      else if (Uppercase(constitutive_model_name) == 'BARO-KO15') then
         if (material_description == 'Hostun Sand 01') then
            !materialparameters(1:7) = [0.5899_dp, 1.0_dp, 2.5076_dp, 1.0_dp, 40.0_dp, 0.91_dp, 0.5_dp]
            !                                             v--- different sign compared to source
            materialparameters(1:7) = [0.5899_dp, 1.0_dp, -2.5076_dp, 1.0_dp, 40.0_dp, 0.91_dp, 0.5_dp]
            is_assigned = .True.
         end if
      !
      else if (Uppercase(constitutive_model_name) == 'BARO-SC18') then
         if (material_description == 'Hostun Sand 01') then
            materialparameters(1:9) = [ &
               0.5899_dp, 430.0_dp, 0.74_dp, 3.0_dp, 0.904_dp, 1.093_dp, 3.0_dp, 5.0_dp, 10.0_dp]
            is_assigned = .True.
         end if
      !
      else if (Uppercase(constitutive_model_name) == 'BARO-KO21') then
         if (material_description == 'Hostun Sand 01') then
            materialparameters(1:10) = [ &
               0.5899_dp, 0.50_dp, -0.20_dp, 5000.0_dp, 0.50_dp, 30.0_dp, 0.0_dp, 1.0_dp, 0.02_dp, 0.54_dp]
            is_assigned = .True.
         end if
      end if

      if (.not. is_assigned) then
         write(*, *) 'No material found for given material_description or constitutive_model_name'
         return
      end if

      call Adjust_Default_Materialparameters(constitutive_model_name=constitutive_model_name, &
         adj_name=adj_name, materialparameters=materialparameters, nu=nu, igran_active=igran_active, &
         success=success)
      if (.not. success) then
         write(*, *) 'No material found for given userroutine flag (if any is set)'
         materialparameters = 0.0_dp
      end if
   end subroutine Get_Material


   ! --------------------------------------------------------------- !
   subroutine Adjust_Default_Materialparameters(constitutive_model_name, &
      adj_name, materialparameters, nu, igran_active, success)
   ! --------------------------------------------------------------- !
      character(len=9), intent(in) :: constitutive_model_name
      character(len=9), intent(out) :: adj_name
      real(dp), dimension(num_fixed_params), intent(inout) :: materialparameters
      real(dp), intent(in) :: nu
      logical, intent(in) :: igran_active
      logical, intent(out) :: success
      ! ------------------------------------------------------------ !
      real(dp), parameter :: pi = 4.0_dp*atan(1.0_dp)

      success = .False.
      adj_name = constitutive_model_name

      if (Uppercase(constitutive_model_name) == 'HYPO-VW96') then
         if (.not. igran_active) then
            materialparameters(9:10) = [1.0_dp, 1.0_dp]
         end if

#ifdef _XMAT
         materialparameters = [ &
            materialparameters(1), &                ! 01 phi_c
            nu, &                                   ! 02 nu
            materialparameters(2:13), &             ! 03-14 h_s, n, e_d0, e_c0, e_i0, alpha, beta, m_T, m_R, R_max, beta_r, chi
            0.0_dp, 0.0_dp]                         ! 15-16
         success = .True.
#else
#if defined(_HYPO) || defined(_TP)
         materialparameters = [ &
            materialparameters(1), &                ! 01 phi_c
            nu, &                                   ! 02 nu
            materialparameters(2:13), &             ! 03-14 h_s, n, e_d0, e_c0, e_i0, alpha, beta, m_T, m_R, R_max, beta_r, chi
            0.0_dp, 0.0_dp]                         ! 15-16
         adj_name = 'WO2_Test'
         success = .True.
#else
#ifdef _UIBK
         materialparameters = [ &
            materialparameters(1)*180.0_dp/pi, &    ! 01 phi_c
            materialparameters(2:8), &              ! 02-08 h_s, n, e_d0, e_c0, e_i0, alpha, beta
            0.0_dp, &                               ! 09 T_c
            materialparameters(11), &               ! 10 R_max
            materialparameters(10), &               ! 11 m_R
            materialparameters(9), &                ! 12 m_T
            materialparameters(12:13), &            ! 13-14 beta_r, chi
            0.0_dp, 0.0_dp]                         ! 15-16
         success = .True.
#else
#ifdef _PLAXIS
         ! Routine uses intergranular strain formulation for m_R > 0.5 instead of m_R > 1.0
         if (.not. igran_active) then
            materialparameters(10) = 0.4_dp
         end if

         materialparameters = [ &
            materialparameters(1)*180.0_dp/pi, &    ! 01 phi_c
            0.0_dp, &                               ! 02 p_t
            materialparameters(2:8), &              ! 03-09 h_s, n, e_d0, e_c0, e_i0, alpha, beta
            materialparameters(10), &               ! 10 m_R
            materialparameters(9), &                ! 11 m_T
            materialparameters(11:13), &            ! 12-14 R_max, beta_r, chi
            0.0_dp, &                               ! 15 bulk_w 
            0.0_dp]                                 ! 16
         success = .True.
#endif
#endif
#endif
#endif
      else if (Uppercase(constitutive_model_name) == 'HYPO-WU92') then
         success = .True.
      else if (Uppercase(constitutive_model_name) == 'BARO-KO15') then
         success = .True.
      else if (Uppercase(constitutive_model_name) == 'BARO-SC18') then
         success = .True.
      else if (Uppercase(constitutive_model_name) == 'BARO-KO21') then
         success = .True.
      end if
   end subroutine Adjust_Default_Materialparameters


   ! --------------------------------------------------------------- !
   subroutine Prepare_State(constitutive_model_name, voidratio, intergranular_strain, &
         igran_active, integration_method, first_dt, integration_tolerance, crit_voidratio, &
         statevariables, success)
   ! --------------------------------------------------------------- !
      character(len=9), intent(in) :: constitutive_model_name
      real(dp), intent(in) :: voidratio
      real(dp), dimension(6), intent(in), optional :: intergranular_strain
      logical, intent(in), optional :: igran_active
      integer, intent(in), optional :: integration_method
      real(dp), intent(in), optional :: first_dt
      real(dp), intent(in), optional :: integration_tolerance
      real(dp), intent(in), optional :: crit_voidratio
      real(dp), dimension(num_fixed_states), intent(out) :: statevariables
      logical, intent(out) :: success
      ! ------------------------------------------------------------ !
      logical :: is_assigned, igran_active_internal
      integer :: integration_method_internal
      real(dp) :: first_dt_internal, integ_tol_internal, crit_voidratio_internal
      real(dp), dimension(6) :: intergr_strain_internal

      if (present(intergranular_strain)) then
         intergr_strain_internal = intergranular_strain
      else
         intergr_strain_internal = 0.0_dp
      end if

      if (present(igran_active)) then
         igran_active_internal = igran_active
      else
         igran_active_internal = .False.
      end if

      if (present(integration_method)) then
         integration_method_internal = integration_method
      else
         integration_method_internal = 1
      end if

      if (present(first_dt)) then
         first_dt_internal = first_dt
      else
         first_dt_internal = 1.0_dp
      end if

      if (present(integration_tolerance)) then
         integ_tol_internal = integration_tolerance
      else
         integ_tol_internal = 0.0001_dp
      end if

      if (present(crit_voidratio)) then
         crit_voidratio_internal = crit_voidratio
      else
         crit_voidratio_internal = 1.0_dp
      end if

      success = .False.
      statevariables = 0.0_dp

      if (Uppercase(constitutive_model_name) == 'HYPO-VW96') then
#ifdef _XMAT
         statevariables = [ &
            voidratio, &                            ! 01 void ratio
            intergr_strain_internal, &              ! 02-10 intergranular strain
            intergr_strain_internal(4:6), &         !
            0.0_dp, 0.0_dp, 0.0_dp, 0.0_dp, 0.0_dp, &
            0.0_dp, 0.0_dp, 0.0_dp, 0.0_dp, 0.0_dp]
         success = .True.
#else
#if defined(_HYPO) || defined(_TP)
         statevariables = [ &
            voidratio, &                            ! 01 void ratio
            0.0_dp, 0.0_dp, 0.0_dp, 0.0_dp, 0.0_dp, &! 02-06
            intergr_strain_internal, &              ! 07-12 intergranular strain
            0.0_dp, 0.0_dp, 0.0_dp, 0.0_dp, 0.0_dp, &
            0.0_dp, 0.0_dp, 0.0_dp]
         success = .True.
#else
#ifdef _UIBK
         statevariables = [ &
            real(integration_method_internal, dp), &! 01 time integration method (1=Eul-Exp, 2=Eul-Imp, 3=Ric-Exp, 4=Ric-Imp)
            first_dt_internal, &                    ! 02 suggested first time substep
            0.0_dp, &                               ! 03 (output) mobilized friction angle
            1.0_dp, &                               ! 04 number of additional scalar variables (1-5)
            1.0_dp, &                               ! 05 number of additional tensor variables (1-3)
            14.0_dp, &                              ! 06 resulting first index of tolerance component (after tensor variables)
            voidratio, &                            ! 07 void ratio
            intergr_strain_internal, &              ! 08-13 intergranular strain
            integ_tol_internal, &                   ! 14 absolute tolerance (stress)
            integ_tol_internal, &                   ! 15 relative tolerance (stress)
            integ_tol_internal, &                   ! 16 absolute tolerance (consistent tangent)
            integ_tol_internal, &                   ! 17 relative tolerance (consistent tangent)
            integ_tol_internal, &                   ! 18 relative tolerance (additional state variables)
            integ_tol_internal, &                   ! 19 absolute tolerance (void ratio)
            integ_tol_internal]                     ! 20 absolute tolerance (intergranular strain)
         if (.not. igran_active_internal) then
            statevariables(5) = 0.0_dp
         end if
         success = .True.
#else
#ifdef _PLAXIS
         statevariables = [ &
            intergr_strain_internal, &              ! 01-06 intergranular strain
            voidratio, &                            ! 07 void ratio
            0.0_dp, &                               ! 08 excess pore pressure
            0.0_dp, &                               ! 09 (output) replacement stiffness
            0.0_dp, 0.0_dp, 0.0_dp, &               ! 10-12
            first_dt_internal, &                    ! 13 time sub increment
            0.0_dp, 0.0_dp, 0.0_dp, 0.0_dp, 0.0_dp, &
            0.0_dp, 0.0_dp]
         success = .True.
#endif
#endif
#endif
#endif
      else if (Uppercase(constitutive_model_name) == 'HYPO-WU92') then
         statevariables(1) = voidratio
         success = .True.
      else if (Uppercase(constitutive_model_name) == 'BARO-KO15') then
         statevariables(1) = voidratio
         success = .True.
      else if (Uppercase(constitutive_model_name) == 'BARO-SC18') then
         statevariables(1) = voidratio
         success = .True.
      else if (Uppercase(constitutive_model_name) == 'BARO-KO21') then
         statevariables(1) = voidratio
         statevariables(2) = crit_voidratio_internal
         success = .True.
      end if

      if (.not. success) then
         write(*, *) 'No statevariables could be prepared for given userroutine flag (if any is set)'
      end if
   end subroutine Prepare_State


   ! --------------------------------------------------------------- !
   subroutine Postprocess_State(constitutive_model_name, inoutstate, nstates, voidratio, &
      intergranular_strain, jacobian)
   ! --------------------------------------------------------------- !
      character(len=9), intent(in) :: constitutive_model_name
      integer, intent(in) :: nstates
      real(dp), dimension(nstates), intent(in) :: inoutstate
      real(dp), intent(out) :: voidratio
      real(dp), dimension(6), intent(out) :: intergranular_strain
      real(dp), dimension(6, 6), intent(inout) :: jacobian
      ! ------------------------------------------------------------ !

      voidratio = 0.0_dp
      intergranular_strain = 0.0_dp

      if (Uppercase(constitutive_model_name) == 'HYPO-VW96') then
#ifdef _XMAT
         if (nstates < 7) then
            write(*, *) 'Postprocess_State: nstates smaller than expected (7), not changing anything'
         else
            voidratio = inoutstate(1)
            intergranular_strain = inoutstate(2:7)
         end if
#else
#if defined(_HYPO) || defined(_TP)
         if (nstates < 12) then
            write(*, *) 'Postprocess_State: nstates smaller than expected (12), not changing anything'
         else
            voidratio = inoutstate(1)
            intergranular_strain = inoutstate(7:12)
         end if
#else
#ifdef _UIBK
         if (nstates < 13) then
            write(*, *) 'Postprocess_State: nstates smaller than expected (13), not changing anything'
         else
            voidratio = inoutstate(7)
            intergranular_strain = inoutstate(8:13)
         end if
         ! Manually adjust the jacobian for UIBK routine
         jacobian(:, 4:6) = 0.5_dp*jacobian(:, 4:6)
#else
#ifdef _PLAXIS
         if (nstates < 7) then
            write(*, *) 'Postprocess_State: nstates smaller than expected (7), not changing anything'
         else
            voidratio = inoutstate(7)
            intergranular_strain = inoutstate(1:6)
         end if
#endif
#endif
#endif
#endif
      else if (Uppercase(constitutive_model_name) == 'HYPO-WU92') then
         if (nstates < 1) then
            write(*, *) 'Postprocess_State: nstates smaller than expected (1), not changing anything'
         else
            voidratio = inoutstate(1)
         end if
      else if (Uppercase(constitutive_model_name) == 'BARO-KO15') then
         if (nstates < 1) then
            write(*, *) 'Postprocess_State: nstates smaller than expected (1), not changing anything'
         else
            voidratio = inoutstate(1)
         end if
      else if (Uppercase(constitutive_model_name) == 'BARO-SC18') then
         if (nstates < 1) then
            write(*, *) 'Postprocess_State: nstates smaller than expected (1), not changing anything'
         else
            voidratio = inoutstate(1)
         end if
      else if (Uppercase(constitutive_model_name) == 'BARO-KO21') then
         if (nstates < 1) then
            write(*, *) 'Postprocess_State: nstates smaller than expected (1), not changing anything'
         else
            voidratio = inoutstate(1)
         end if
      end if
   end subroutine Postprocess_State


   ! --------------------------------------------------------------- !
   pure function Uppercase(text) result(upper)
   ! --------------------------------------------------------------- !
      character(len=*), intent(in) :: text
      character(len=len(text)) :: upper
      ! ------------------------------------------------------------ !
      character(len=26), parameter :: low_alph = 'abcdefghijklmnopqrstuvwxyz'
      character(len=26), parameter :: up_alph = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
      integer :: idx, pos

      upper = text
      do idx = 1, len(text)
         pos = index(low_alph, text(idx:idx))
         if (pos /= 0) then
            upper(idx:idx) = up_alph(pos:pos)
         end if
      end do
   end function Uppercase
end module Preparation
