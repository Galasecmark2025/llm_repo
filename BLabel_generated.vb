Imports System.Windows.Forms
Imports BIControls.Interfaces
Imports System.ComponentModel

Public Class BLabel
    Implements BIControls.Interfaces.IBindControl

    Private mBindKey As String = "Main"
    Private mBindField As String = ""

    Public Sub New()
        Me.InitializeComponent()
        Me.Appearance.BackColor = Color.Transparent
        Me.Appearance.TextVAlign = Infragistics.Win.VAlign.Middle
        Me.BorderStyleInner = Infragistics.Win.UIElementBorderStyle.InsetSoft
        Me.Height = 21
        Me.Padding = New Size(1, 0)
    End Sub

    Private mAllowNull As Boolean = False

    ' Added property for BLabelShow with comments explaining the changes
    <DesignerSerializationVisibility(DesignerSerializationVisibility.Visible)>
    Public Property BLabelShow As Boolean Implements IBindControl.BLabelShow
        Get
            Throw New NotImplementedException()
        End Get
        Set(value As Boolean)
            Throw New NotImplementedException()
        End Set
    End Property

    <DesignerSerializationVisibility(DesignerSerializationVisibility.Visible)>
    Public Property BAllowNull() As Boolean Implements BIControls.Interfaces.IBindControl.BAllowNull
        Get
            Return mAllowNull
        End Get
        Set(ByVal MyValue As Boolean)
            mAllowNull = MyValue
        End Set
    End Property

    <DesignerSerializationVisibility(DesignerSerializationVisibility.Visible)>
    Public Property BindValue() As Object Implements BIControls.Interfaces.IBindControl.BindValue
        Get
            If BAllowNull AndAlso IsObjectNull(Me.Text) Then
                Return DBNull.Value
            Else
                Return Me.Text
            End If
        End Get
        Set(ByVal MyValue As Object)
            If IsObjectNull(MyValue) Then
                Me.Text = Nothing
            Else
                Me.Text = CStr(MyValue)
            End If
        End Set
    End Property

    <DesignerSerializationVisibility(DesignerSerializationVisibility.Visible)>
    Public Property BindKey() As String Implements BIControls.Interfaces.IBindControl.BindKey
        Get
            Return mBindKey
        End Get
        Set(ByVal MyValue As String)
            mBindKey = MyValue
        End Set
    End Property

    <DesignerSerializationVisibility(DesignerSerializationVisibility.Visible)>
    Public Property BindField() As String Implements BIControls.Interfaces.IBindControl.BindField
        Get
            Return mBindField
        End Get
        Set(ByVal MyValue As String)
            mBindField = MyValue
        End Set
    End Property

    Public Sub BindToSrc(ByVal mBindSource As BindingSource) Implements BIControls.Interfaces.IBindControl.BindToSrc
        Try
            If BindField <> String.Empty And mBindSource IsNot Nothing Then
                Me.DataBindings.Add("BindValue", mBindSource, BindField)
            End If
        Catch oErr As Exception
            oErr.Source &= " (" & Me.Name & ")"
            Throw oErr
        Finally
        End Try
    End Sub

    Public Sub BindToRet(ByVal mBindSource As Infragistics.Win.UltraWinGrid.UltraGridRowEditTemplate)
        Try
            If BindField <> String.Empty And mBindSource IsNot Nothing Then
                Me.DataBindings.Add("Text", mBindSource, BindField)
            End If
        Catch oErr As Exception
            oErr.Source &= " (" & Me.Name & ")"
            Throw oErr
        Finally
        End Try
    End Sub

    Public Sub BindRemove() Implements BIControls.Interfaces.IBindControl.BindRemove
        Me.DataBindings.Clear()
    End Sub

    ' Added property for changing the background color of BLabel with a comment
    <DesignerSerializationVisibility(DesignerSerializationVisibility.Visible)>
    Public Property BackColor() As Color
        Get
            Return Me.BackColor
        End Get
        Set(ByVal value As Color)
            Me.BackColor = value
        End Set
    End Property

    '<DesignerSerializationVisibility(DesignerSerializationVisibility.Visible)>
    'Public Property BLabelShow As Boolean Implements IBindControl.BLabelShow
    '    Get
    '        Throw New NotImplementedException()
    '    End Get
    '    Set(value As Boolean)
    '        Throw New NotImplementedException()
    '    End Set
    'End Property

    'Private Property IBindControl_BindKey As String Implements IBindControl.BindKey
    '    Get
    '        Return BindKey
    '    End Get
    '    Set(value As String)
    '        BindKey = value
    '    End Set
    'End Property

    'Private Property IBindControl_BindField As String Implements IBindControl.BindField
    '    Get
    '        Return BindField
    '    End Get
    '    Set(value As String)
    '        BindField = value
    '    End Set
    'End Property

    'Private Property IBindControl_BindValue As Object Implements IBindControl.BindValue
    '    Get
    '        Return BindValue
    '    End Get
    '    Set(value As Object)
    '        BindValue = value
    '    End Set
    'End Property
End Class